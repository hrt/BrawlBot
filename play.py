import time
from memorpy import MemWorker, Process
from offsets import *
from utils import dereference_offsets, probe_entities, fetch_entity
import keyboard

def main():
    mem = MemWorker(name=PROCESS_NAME)

    g_input_ptr = dereference_offsets(mem, g_input_offsets)
    g_input = mem.Address(g_input_ptr + g_input_base_offset)
    local_ptr = dereference_offsets(mem, local_ptr_offsets)
    print('g_input: %s' % hex(g_input))
    print('local_ptr: %s' % hex(local_ptr))

    entity_pointers = probe_entities(mem, g_input)

    print('Removing local entity from entity list')
    entity_pointers.remove(local_ptr)

    def calculate_actual_input():
        # based on my settings for brawlhalla
        val = 0
        val |= LEFT * keyboard.is_pressed('LEFT')
        val |= RIGHT * keyboard.is_pressed('RIGHT')
        val |= UP * keyboard.is_pressed('UP')
        val |= DOWN * keyboard.is_pressed('DOWN')
        val |= DODGE * keyboard.is_pressed('x')
        val |= THROW * keyboard.is_pressed('e')
        val |= QUICK_ATTACK * keyboard.is_pressed('q')
        val |= HEAVY_ATTACK * keyboard.is_pressed('w')
        return val

    def reset_input(address, hard=False, u=0):
        if hard:
            address.write(0)
            time.sleep(0.03)
        time.sleep(0.03)
        address.write(calculate_actual_input() | u)

    def fetch_local():
        return fetch_entity(mem, local_ptr)

    def fetch_entity_from_index(i):
        return fetch_entity(mem, entity_pointers[i])

    def down_quick(local, target, u=0):
        target_direction = LEFT if local.x-target.x > 0 else RIGHT
        g_input.write(target_direction | DOWN | QUICK_ATTACK | u)

    def neutral_heavy(local, target):
        target_direction = LEFT if local.x-target.x > 0 else RIGHT
        if target_direction != local.direction:
            g_input.write(target_direction)
            reset_input(g_input)
        g_input.write(HEAVY_ATTACK)
        reset_input(g_input)

    def neutral_quick(local, target):
        target_direction = LEFT if local.x-target.x > 0 else RIGHT
        if target_direction != local.direction:
            g_input.write(target_direction)
            reset_input(g_input)
        g_input.write(QUICK_ATTACK)
        reset_input(g_input)

    def side_air_quick(local, target, u=UP):
        target_direction = LEFT if local.x-target.x > 0 else RIGHT
        g_input.write(target_direction | u | QUICK_ATTACK)

    def side_quick(local, target, u=UP):
        target_direction = LEFT if local.x-target.x > 0 else RIGHT
        g_input.write(target_direction | QUICK_ATTACK)

    def air_quick(local, target, u=UP):
        g_input.write(QUICK_ATTACK)

    def gravity_cancel():
        print('gravity cancel')
        g_input.write(DODGE)
        reset_input(g_input)
        time.sleep(0.1)

    print('Entering script mode')
    while True:
        local = fetch_local()
        if local.in_animation or local.in_stun:
            continue
        targets = [fetch_entity_from_index(i) for i in range(len(entity_pointers))]
        current_input = g_input.read()
        for target in targets:
            dx = target.x-local.x
            dy = target.y-local.y
            if target.can_dodge and target.in_attack and abs(dx+target.x_vel-local.x_vel) < 200 and abs(dy+target.y_vel-local.y_vel) < 200 and local.can_dodge:
                print('phase dodge')
                if local.not_grounded:
                    g_input.write(DODGE | calculate_actual_input())
                else:
                    g_input.write(DODGE)
                time.sleep(0.05)
                reset_input(g_input)
                break

            if local.weapon == MELEE:
                # jump if above near
                if (150 < dy < 200) and (0 < abs(dx) < 250) and local.jump_count < 2 and target.in_stun:
                    print('jump if above near')
                    target_direction = LEFT if local.x-target.x > 0 else RIGHT
                    g_input.write(UP | target_direction)
                    reset_input(g_input)
                    break

                # neutral quick
                if (abs(dy) < 150) and (0 < abs(dx) < 150) and not local.not_grounded:
                    print('neutral quick')
                    neutral_quick(local, target)
                    reset_input(g_input)
                    break

                # side quick
                if (abs(dy) < 150) and (50 < abs(dx) < 350) and not local.not_grounded and target.in_stun:
                    print('side quick')
                    side_quick(local, target)
                    reset_input(g_input)
                    break

                # down quick
                if (abs(dy) < 150) and (100 < abs(dx) < 350) and not local.not_grounded:
                    print('down quick')
                    down_quick(local, target)
                    reset_input(g_input)
                    break

                # quick
                if (abs(dy) < 50) and (10 < abs(dx) < 250) and local.not_grounded:
                    print('air quick')
                    air_quick(local, target)
                    reset_input(g_input)
                    break

                if -100 > dy > -350 and 350 > abs(dx) > 200 and local.not_grounded:
                    print('air down quick')
                    down_quick(local, target)
                    reset_input(g_input)
                    break


            if local.weapon == SPEAR:
                if 100 < dy < 350 and 600 > abs(dx) > 100 and target.damage_taken > 180:
                    print('spear finish')
                    if local.not_grounded and local.can_dodge:
                        gravity_cancel()
                        neutral_heavy(local, target)
                        break
                    elif not local.not_grounded:
                        neutral_heavy(local, target)

                if 100 < dy < 350 and 350 > abs(dx) > 100:
                    print('down quick')
                    if local.not_grounded and local.can_dodge:
                        gravity_cancel()
                        down_quick(local, target)
                        reset_input(g_input)
                        break
                    elif not local.not_grounded:
                        down_quick(local, target)
                        reset_input(g_input)
                        break

                # spear air side quick
                if 200 < dy < 400 and 400 > abs(dx) > 100 and local.not_grounded:
                    print('air side quick')
                    # can be better with jump count (can jump)
                    side_air_quick(local, target)
                    reset_input(g_input)
                    break

                # spear air quick
                if abs(dy) < 200 and 200 > abs(dx) and local.not_grounded:
                    print('air quick')
                    # can be better with jump count (can jump)
                    air_quick(local, target)
                    reset_input(g_input)
                    break

                # quick
                if (abs(dy) < 150) and (100 < abs(dx) < 600) and not local.not_grounded:
                    print('side quick')
                    side_quick(local, target)
                    reset_input(g_input)
                    break


            if local.weapon == SWORD:
                if 300 < (dy+target.y_vel-local.y_vel) < 450 and 350 > abs(dx+target.x_vel-local.x_vel) > 200 and target.damage_taken > 180:
                    print('sword finish')
                    if local.not_grounded and local.can_dodge:
                        gravity_cancel()
                        neutral_heavy(local, target)
                        break
                    elif not local.not_grounded:
                        neutral_heavy(local, target)
                        break

                if 100 < dy < 350 and 350 > abs(dx) > 100 and target.in_stun and target.damage_taken > 180:
                    print('sword stun finish')
                    if local.not_grounded and local.can_dodge:
                        gravity_cancel()
                        neutral_heavy(local, target)
                        reset_input(g_input)
                        break
                    elif not local.not_grounded:
                        neutral_heavy(local, target)
                        reset_input(g_input)
                        break

                # jump if above near
                if (100 < dy < 200) and (0 < abs(dx) < 200) and local.jump_count < 2 and target.in_stun:
                    print('jump if above near')
                    target_direction = LEFT if local.x-target.x > 0 else RIGHT
                    g_input.write(UP | target_direction)
                    reset_input(g_input)
                    break

                # air down quick
                if (-250 < dy < -50) and (0 < abs(dx) < 150) and local.not_grounded and local.jump_count < 2:
                    print('air down quick')
                    target_direction = LEFT if local.x-target.x > 0 else RIGHT
                    down_quick(local, target)
                    reset_input(g_input)
                    break

                # air quick
                if (100 < dy < 350) and (0 < abs(dx) < 200) and local.not_grounded:
                    print('air quick')
                    air_quick(local, target)
                    reset_input(g_input)
                    break

                # air side quick
                if (abs(dy) < 100) and (70 < abs(dx) < 350) and local.not_grounded and local.jump_count < 2:
                    print('air side quick')
                    target_direction = LEFT if local.x-target.x > 0 else RIGHT
                    side_air_quick(local, target, u=0)
                    reset_input(g_input)
                    break

                # down quick
                if (abs(dy) < 150) and (100 < abs(dx) < 350) and not local.not_grounded:
                    print('down quick')
                    down_quick(local, target)
                    reset_input(g_input)
                    break


            if (target.in_animation and not target.in_stun) and abs(dx+target.x_vel-local.x_vel) < 400 and abs(dy+target.y_vel-local.y_vel) < 400 and local.jump_count < 2:
                print('jump dodge')
                if current_input & UP:
                    reset_input(g_input, u=UP)
                else:
                    g_input.write(UP)
                reset_input(g_input)
                break

main()