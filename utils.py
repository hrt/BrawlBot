from offsets import *
from memorpy.WinStructures import PAGE_READWRITE
import re

from collections import namedtuple
Entity = namedtuple('Entity', 'x y can_dodge not_grounded in_animation in_stun direction weapon jump_count, damage_taken x_vel y_vel in_attack increased_gravity in_edging')

def is_base_of_entity(mem, address):
    # verify entity by checking for recursive pointer
    try:
        ptr = address
        for offset in recursive_ptr_offsets:
            ptr = mem.Address(ptr + offset).read()
        if ptr != address:
            return False
    except:
        return False
    else:
        return True

def aob_scan(mem, entity_pointers, start, size, pattern=None, offset=0, entity_check=False):
    all_the_bytes = mem.process.read(mem.Address(start), type='bytes', maxlen=size)
    matches = re.finditer(pattern, all_the_bytes)
    for match in matches:
        span = match.span()
        if span:
            address = start + span[0] + offset
            if not entity_check:
                entity_pointers.append(address)
            elif address not in entity_pointers and is_base_of_entity(mem, address):
                    entity_pointers.append(address)

def dereference_offsets(mem, name_and_offsets):
    modules = mem.process.list_modules()
    name, offsets = name_and_offsets
    ptr = modules[name]
    for offset in offsets:
        ptr = mem.process.read(mem.Address(ptr + offset))
    return ptr

def entities_aob_scan(mem):
    print('Scanning memory for entities')
    modules = mem.process.list_modules()
    regions = mem.process.iter_region(start_offset=modules[PROCESS_NAME], protec=PAGE_READWRITE)
    entity_pointers = []
    print("Performing deep scan")
    for start, size in regions:
        if len(entity_pointers) >= 4:
            break
        aob_scan(mem, entity_pointers, start, size, pattern=entity_sig_2, offset=1, entity_check=True)

    print('Found %d entities : %s' % (len(entity_pointers), ', '.join([hex(e) for e in entity_pointers])))
    return entity_pointers

def ginput_aob_scan(mem):
    print('Scanning memory for ginput')
    modules = mem.process.list_modules()
    regions = mem.process.iter_region(start_offset=modules[PROCESS_NAME], protec=PAGE_READWRITE)
    ginput_pointers = []
    print("Performing deep scan")
    for start, size in regions:
        if len(ginput_pointers) >= 1:
            break
        aob_scan(mem, ginput_pointers, start, size, pattern=ginput_sig, offset=-16)

    print('Found %d ginput : %s' % (len(ginput_pointers), ', '.join([hex(e) for e in ginput_pointers])))
    assert len(ginput_pointers) == 1, "invalid number of ginput pointers found, find a better sig"
    ginput_pointer = ginput_pointers[0]
    print('g_input: %s' % hex(ginput_pointer))
    return ginput_pointers[0]

def fetch_entity(mem, address):
    x = mem.Address(address + x_offset).read(type='double')
    y =-mem.Address(address + y_offset).read(type='double') # invert it for brain convenience

    increased_gravity = mem.Address(address + increased_gravity_offset).read()
    can_dodge = 0 if mem.Address(address + dodge_offset).read() else 1
    # not_grounded = mem.Address(address + not_grounded_offset).read()
    in_edging = mem.Address(address + in_edging_offset).read()
    not_grounded = mem.Address(address + in_air_offset).read()
    in_animation = mem.Address(address + in_animation_offset).read()
    in_attack = mem.Address(address + in_attack_offset).read()
    in_stun = mem.Address(address + stun_offset).read()
    direction =  LEFT if mem.Address(address + direction_offset).read() else RIGHT
    weapon_ptr = address
    for offset in weapon_ptr_offsets:
        weapon_ptr = mem.Address(weapon_ptr + offset).read()
    jump_count = mem.Address(address + jump_count_offset).read()
    damage_taken = mem.Address(address + damage_taken_offset).read(type='double')
    y_vel = mem.Address(address + y_vel_offset).read(type='double')
    x_vel = mem.Address(address + x_vel_offset).read(type='double')
    return Entity(x+(2*x_vel), y-(2*y_vel), can_dodge, not_grounded, in_animation, in_stun, direction, weapon_ptr, jump_count, damage_taken, x_vel, y_vel, in_attack, increased_gravity, in_edging)
