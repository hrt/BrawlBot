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

def aob_scan(mem, entity_pointers, last_start, last_size, pattern=None, offset=1):
    all_the_bytes = mem.process.read(mem.Address(last_start), type='bytes', maxlen=last_size)
    matches = re.finditer(pattern if pattern else aob_sig_1, all_the_bytes)
    for match in matches:
        span = match.span()
        if span:
            address = last_start + span[0] + offset
            if address not in entity_pointers and is_base_of_entity(mem, address):
                    entity_pointers.append(address)

def dereference_offsets(mem, name_and_offsets):
    modules = mem.process.list_modules()
    name, offsets = name_and_offsets
    ptr = modules[name]
    for offset in offsets:
        ptr = mem.process.read(mem.Address(ptr + offset))
    return ptr

def probe_entities(mem, local_ptr):
    print('Scanning memory for entities')
    modules = mem.process.list_modules()
    regions = mem.process.iter_region(start_offset=modules[PROCESS_NAME], protec=PAGE_READWRITE)
    entity_pointers = []
    starts = []
    sizes = []
    print("Performing quick scan")
    for start, size in regions:
        if len(entity_pointers) >= 4:
            break
        starts.append(start)        
        sizes.append(size)        
        if start < local_ptr:
            continue
        aob_scan(mem, entity_pointers, starts[-10], sizes[-10])

    print('Found %d entities : %s' % (len(entity_pointers), ', '.join([hex(e) for e in entity_pointers])))

    print("Performing deep scan")
    for start, size in zip(starts,sizes):
        if len(entity_pointers) >= 4:
            break
        aob_scan(mem, entity_pointers, start, size, pattern=aob_sig_2)

    print('Found %d entities : %s' % (len(entity_pointers), ', '.join([hex(e) for e in entity_pointers])))
    return entity_pointers

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
