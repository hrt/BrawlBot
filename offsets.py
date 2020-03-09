PROCESS_NAME = 'Brawlhalla.exe'
# search for double 568.99 on demon map - it is your standing y
# ginput is just 0 ORed with whatever button you have pressed for example if you have up pressed then it'll be 17

entity_sig_1 = b"\x00\x90\x64......\xA0.......\x00" # base entity -1
entity_sig_2 = b"\x00.\x64..............\x00" # a looser variant
# 90 AD 83 04 10 EF 57 13 50 78 68 07 90 64 C2 62
# 90 AD 57 04 40 32 2C 12 50 58 46 07 90 64 C2 62
# 90 AD E0 03 10 7F 9B 12 50 B8 B3 06 90 64 C2 62
# 90 AD BC 03 10 FF 84 12 50 88 97 06 90 64 C2 62
# 90 AD 2F 04 10 0F F3 12 50 78 17 07 90 64 C2 62
# 90 AD EE 03 10 9F 8C 12 50 88 AA 06 90 64 A3 62
ginput_sig = b"\x90\xAD......\x50...\x90\x64.\x62"
g_input_base_offset = 0x34 # add to the base of ginput
g_input_offsets = ('Adobe AIR.dll', [0x0131550C, 0x1DC, 0x18, 0x8, 0x98, 0x1F8, 0x4CC])
local_ptr_offsets = ('Adobe AIR.dll', [0x01315528, 0xA4, 0x44C, 0x14, 0x98, 0x98, 0x548])

# below are relative to base of entity
increased_gravity_offset = 0xC4 # 1 if sprinting down
dodge_offset = 0x154 # 0 if can dodge
in_air_offset = 0x108 # 1 if in air
not_grounded_offset = 0xF4 # 1 if in air
in_attack_offset = 0x88 # 1 if attacking, also affected by dodge
in_animation_offset = 0xA0 # 1 if in animation
in_edging_offset = 0x118 # 2 if edging
x_offset = 0x378
y_offset = 0x370 # up is negative
stun_offset = 0x184 # positive if stunned
direction_offset = 0xD4 # 1 LEFT or 0 RIGHT
jump_count_offset = 0x1F0 # 0, 1, 2 (2 means no jumps left)
damage_taken_offset = 0x418
y_vel_offset = 0x320 # negative up
x_vel_offset = 0x328 # negative left
recursive_ptr_offsets = [0x268, 0x4c]
weapon_ptr_offsets = [0x2BC, 0x44, 0x8]

QUICK_ATTACK = 640
HEAVY_ATTACK = 64
UP = 17
DOWN = 2
LEFT = 4
RIGHT = 8
DODGE = 256
THROW = 516
SPEAR = 0x00005F77
SWORD = 0x00004222
KATAR = 25411
MELEE = 14969