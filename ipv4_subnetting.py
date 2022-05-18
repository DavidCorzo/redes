from lib2to3.pytree import convert
import re
import time
import os
import math 
from termcolor import colored


class subnetting_ipv4:
    def __init__(self, ip_address:str, subnet_mask:int, subnet_count:int=None, hosts_count:int=None):
        self.ip_address         = ip_address
        self.subnet_mask        = self.convert_subnet_mask(subnet_mask)
        self.subnet_count       = subnet_count
        self.hosts_count        = hosts_count
        self.ip_octets          = None
        self.ip_binary_octets   = None
        self.ip_binary_string   = None
        self.bits_for_hosts     = None
        self.bits_for_subnet    = None
        self.new_subnet_mask    = None
        self.bn_addresses_bin = list()
        self.bn_addresses_dec = list()
        
        self.get_ip_octets()
        self.get_binary_octets()
        self.get_ip_binary_string()
        self.determine_subnets_and_hosts()
        self.get_broadcast_network_addresses()

        # print(
        #     f'ip_address({self.ip_address})\n' +
        #     f'subnet_mask({self.subnet_mask})\n' +
        #     f'subnet_count({self.subnet_count})\n' +
        #     f'hosts_count({self.hosts_count})\n' +
        #     f'ip_octets({self.ip_octets})\n' +
        #     f'ip_binary_octets({self.ip_binary_octets})\n' +
        #     f'ip_binary_string({self.ip_binary_string})\n' +
        #     f'bits_for_hosts({self.bits_for_hosts})\n' +
        #     f'bits_for_subnet({self.bits_for_subnet})\n' +
        #     f'new_subnet_mask({self.new_subnet_mask})\n'
        # )
    
    def convert_subnet_mask(self, subnet_mask):
        converted_subnet_mask = None
        if isinstance(subnet_mask, str):
            if re.match(r'^/?\d+$', subnet_mask):
                converted_subnet_mask = int(subnet_mask.replace('/',''))
            elif re.match(r'^\d\d?\d?\.\d\d?\d?\.\d\d?\d?\.\d\d?\d?$', subnet_mask):
                split_mask_bin = tuple(bin(int(s)).replace('0b','').zfill(8) for s in subnet_mask.split('.'))
                mask_bin_string = ''.join(split_mask_bin)
                if len(mask_bin_string) == 32:
                    if re.match(r'^1+0+$', mask_bin_string):
                        converted_subnet_mask = mask_bin_string.count('1')
                    else:
                        print("## ERROR: subnet mask does not have a constant stream of 1's followed by 0's.")
                        exit(0)
                else:
                    print("## ERROR: mask does not have length of 32.")
                    exit(0)
            else:
                print(f"## ERROR: Unrecognized format of subnet mask {subnet_mask}")
                exit(0)
        elif isinstance(subnet_mask, int):
            converted_subnet_mask = int(subnet_mask)
        else:
            print("## ERROR: Unrecognized object of subnet mask {subnet_mask}")
            exit(0)
        
        if converted_subnet_mask not in range(0, 32):
            print(f"## ERROR: subnet mask must be in range 0-31.")
            exit(0)
        
        return converted_subnet_mask
        

    def get_ip_octets(self):
        '''
        1. Checks if the ip matches the regex.
        2. Splits the ip into its octets.
        3. Checks if each octet is within 0 to 255.
        4. If everything went well return tuple of 4 containing the decimal representations of each of the octets, else return None.
        '''
        if not re.match(r'\d\d?\d?\.\d\d?\d?\.\d\d?\d?\.\d\d?\d?', self.ip_address):
            print(f"## ERROR: ip address={self.ip_address} is in an incorrect format.\n\tPlease enter ip adress as the example: 128.0.0.0.")
            exit(0)
        self.ip_octets = tuple(int(num) for num in self.ip_address.split('.'))
        invalid_range = False
        for index, octet in enumerate(self.ip_octets):
            if (octet not in range(0, 256)):
                invalid_range = True
                print(f"## ERROR: In ip {self.ip_address}, the octet's at index={index}, \"{octet}\", is incorrect. Octet need to be within range of 0 to 255.")
        if invalid_range:
            exit(0)
        
    def get_binary_octets(self):
        '''
        1. Assumes that the self.get_ip_octets has been executed.
        2. Then gets the binary representations of each octet and stores it in a list.
        '''
        self.ip_binary_octets = tuple(bin(x).replace('0b','').zfill(8) for x in self.ip_octets)

    def get_ip_binary_string(self):
        '''
        1. Assumes that the self.get_binary_octets method has been executed.
        2. Then gets the binary string representation for the ip address.
        '''
        self.ip_binary_string = ''.join(self.ip_binary_octets)
        if len(self.ip_binary_string) != 32:
            print("## ERROR: binary string is not 32 characters long.")
            exit(0)

    def bits_required_for_num(self, num):
        '''
        Calculates the amount of bits required to store a number given.
        '''
        bits = 1
        q = 0
        while True:
            q = pow(2, bits)
            if q >= num:
                break
            else:
                bits += 1
        return bits

    
    def determine_subnets_and_hosts(self):
        subnet_c_null = self.subnet_count is None
        hosts_c_null = self.hosts_count is None
        if (subnet_c_null) and (hosts_c_null):
            print(f"No subnets and no hosts amounts were specified.")
            exit(-1)
        
        available_bits = 32 - self.subnet_mask
        if (subnet_c_null ^ hosts_c_null):
            if subnet_c_null:
                self.bits_for_hosts  = self.bits_required_for_num(self.hosts_count)
                self.bits_for_subnet = abs(available_bits - self.bits_for_hosts)
                if (self.bits_for_subnet == 0):
                    print(f"ERROR: There is no space for the subnet portion host_portion({self.bits_for_hosts}) of {available_bits} available bits, too large.")
                    exit(0)
                self.subnet_count = pow(2, self.bits_for_subnet)
            elif hosts_c_null:
                self.bits_for_subnet = self.bits_required_for_num(self.subnet_count)
                self.bits_for_hosts = abs(available_bits - self.bits_for_subnet)
                if (self.bits_for_hosts == 0):
                    print(f"ERROR: There is no space for the host portion subnet_portion({self.bits_for_subnet}) of {available_bits} available bits, too large.")
                    exit(0)
                self.hosts_count = pow(2, self.bits_for_hosts)
            else:
                print("This should never get executed.")
        else: # both are specified
            self.bits_for_hosts = self.bits_required_for_num(self.hosts_count)
            self.bits_for_subnet = self.bits_required_for_num(self.subnet_count)
            if (self.bits_for_hosts + self.bits_for_subnet) > available_bits:
                print(f"OVERFLOW: Bits available are {available_bits}, the bits required for subnet {self.bits_for_subnet} and bits required for {self.bits_for_hosts} exceed the available bits.")
                exit(0)
            self.bits_for_subnet = available_bits - self.bits_for_hosts
            self.subnet_count    = pow(2, self.bits_for_subnet)
            self.hosts_count     = pow(2, self.bits_for_hosts)
        self.new_subnet_mask     = self.subnet_mask + self.bits_for_subnet

    def get_broadcast_network_addresses(self):
        for subnet in range(self.subnet_count):
            ip_masked = self.ip_binary_string[0:self.subnet_mask]
            subnet_portion = bin(subnet).replace('0b','').zfill(self.bits_for_subnet)
            host_portion_n = f"{'0'*self.bits_for_hosts}"
            host_portion_b = f"{'1'*self.bits_for_hosts}"
            network_address_bin = tuple((ip_masked, subnet_portion, host_portion_n))
            broadcast_address_bin = tuple((ip_masked, subnet_portion, host_portion_b))
            self.bn_addresses_bin.append(tuple((network_address_bin, broadcast_address_bin)))
            na_str = '.'.join([f'{int(x, 2)}'.replace('0b','').zfill(3) for x in re.findall('........', (ip_masked + subnet_portion + host_portion_n))])
            ba_str = '.'.join([f'{int(x, 2)}'.replace('0b','').zfill(3) for x in re.findall('........', (ip_masked + subnet_portion + host_portion_b))])
            self.bn_addresses_dec.append(tuple((na_str, ba_str)))

            
if __name__ == '__main__':
    os.system('cls')
    print(colored(text=f'1. Welcome to the subnetting calculator.', color='red', attrs=['reverse', 'blink']))
    input()
    os.system('cls')
    ip_address   = "10.10.0.0" # input(f'Enter an ipv4 address: ')
    subnet_mask  = "255.255.0.0" # input(f'Enter a subnet mask: ')
    subnet_count = int("10") # input(f'Required number of subnets: ')
    host_count   = int("10") # input(f'Required number of hosts: ')
    s = subnetting_ipv4(ip_address=ip_address, subnet_mask=subnet_mask, subnet_count=subnet_count, hosts_count=host_count)
    # os.system('cls')
    # explaining the portions of the ip
    print(colored(text=f'2. Turning IP to binary', color='yellow', attrs=['reverse', 'blink']))
    # convert to binary:
    print(
        f'First we will turn the IP to binary, for this just grab each of the four octets \n'
        f'written in decimal and convert to binary: ip_address={colored(s.ip_address, color="red", attrs=["reverse", "blink"])} -> ip_address binary={colored(".".join(s.ip_binary_octets), color="green", attrs=["reverse", "blink"])}' 
    )

    input()
    os.system('cls')

    print(colored(text=f'3. IP portions', color='green', attrs=['reverse', 'blink']))
    print(
        f'An ip has 3 parts when subnetted. {colored("Network portion (blue)", color="blue")}, the {colored("subnet portion (red)", color="red")}, and the {colored("host portion (green)", color="green")}.\n' +
        f'For the IP you entered it would be like so: ' +
        colored(text=f'{s.ip_binary_string[0:s.subnet_mask]}', color='blue', attrs=['reverse', 'blink']) +
        colored(text=f'{s.ip_binary_string[s.subnet_mask-1:s.subnet_mask-1+s.bits_for_subnet]}', color='red', attrs=['reverse', 'blink']) +
        colored(text=f'{s.ip_binary_string[s.subnet_mask+s.bits_for_subnet:]}', color='green', attrs=['reverse', 'blink'])
    )

    input()
    os.system('cls')
    print(
        "\n\n\t\t\t"+
        colored(text=f'{s.ip_binary_string[0:s.subnet_mask]}', color='blue', attrs=['reverse', 'blink']) +
        colored(text=f'{s.ip_binary_string[s.subnet_mask-1:s.subnet_mask+s.bits_for_subnet]}', color='red', attrs=['reverse', 'blink']) +
        colored(text=f'{s.ip_binary_string[s.subnet_mask+s.bits_for_subnet:]}', color='green', attrs=['reverse', 'blink'])
    )

    print(
        f'The network portion (blue) we cannot touch nor modify, this is reserved for internet forwarding.\n' +
        f'The subnet portion (red) is the part where the subnets will be indicated.\n' +
        f'The host portion (green) is the part where the hosts will be indicated.\n'
    )

    input()
    os.system('cls')

    print(colored(text=f'4. Calculating subnet network and broadast addresses', color='red', attrs=['reverse', 'blink']))
    print(
        f'Now we calculate the network addresses and the broadcast addresses of each subnet, \n'
        f'The network address is indicated when the host portion has all 0s\n' +
        f'The broadcast address is indicated when the host portion has all 1s\n' +
        f'Let\'s see it in action.'
    )

    input()
    os.system('cls')

    print('Press q to quit the animation.\n\n\t\t\t')

    index = 0
    NETWORK, BROADCAST = 0, 1
    while True:
        choice = input()
        if (choice == 'q') or (index >= len(s.bn_addresses_bin)):
            break
        if (choice == ''):
            os.system('cls')
            print('Press q to quit the animation.\n\n\t\t\t')
        ip_address_n, ip_address_b = s.bn_addresses_bin[index][NETWORK], s.bn_addresses_bin[index][BROADCAST]
        print(
            f'Network address:   ' +
            colored(text=f'{ip_address_n[0]}', color='blue', attrs=['reverse', 'blink']) +
            colored(text=f'{ip_address_n[1]}', color='red', attrs=['reverse', 'blink']) +
            colored(text=f'{ip_address_n[2]}', color='green', attrs=['reverse', 'blink'])
        )
        print(
            f'Broadcast address: ' +
            colored(text=f'{ip_address_b[0]}', color='blue', attrs=['reverse', 'blink']) +
            colored(text=f'{ip_address_b[1]}', color='red', attrs=['reverse', 'blink']) +
            colored(text=f'{ip_address_b[2]}', color='green', attrs=['reverse', 'blink'])
        )
        index += 1
    
    os.system('cls')
    print(colored(text=f'5. Converting our subnets back to decimal notation.', color='green', attrs=['reverse', 'blink']))
    print(
        f'The 32 bit string presented is divided into 4 sections of 8 bits.\n' +
        f'So lets divide the sections.\n' +
        f'{s.ip_binary_string} -> {s.ip_binary_string[0:8]}.{s.ip_binary_string[8:16]}.{s.ip_binary_string[16:24]}.{s.ip_binary_string[24:]}\n'
        f'Convert to decimal each section:\n' +
        f'{s.ip_binary_string[0:8]}.{s.ip_binary_string[8:16]}.{s.ip_binary_string[16:24]}.{s.ip_binary_string[24:]} -> {int(s.ip_binary_string[0:8], 2)}.{int(s.ip_binary_string[8:16], 2)}.{int(s.ip_binary_string[16:24], 2)}.{int(s.ip_binary_string[24:], 2)}'
        f'Let\'s do the same for network addresses and broadcast addresses.\n'
    )


    os.system('cls')
    print(colored(text=f'6. Converting network and broadcast addresses back to decimal notation.', color='yellow', attrs=['reverse', 'blink']))
    print(f'Let\'s see the animation again but the addresses in decimal form.\n')

    input()
    os.system('cls')

    while True:
        choice = input()
        if (choice == 'q') or (index >= len(s.bn_addresses_bin)):
            break
        if (choice == ''):
            os.system('cls')
            print('Press q to quit the animation.\n\n\t\t\t')
        ip_address_n, ip_address_b = s.bn_addresses_dec[index][NETWORK], s.bn_addresses_dec[index][BROADCAST]
        print(
            f'Network address:   ' +
            colored(text=f'{ip_address_n}', color='blue', attrs=['reverse', 'blink'])
        )
        print(
            f'Broadcast address: ' +
            colored(text=f'{ip_address_b}', color='blue', attrs=['reverse', 'blink'])
        )
        index += 1
    
    os.system('cls')
    print(colored(text=f'7. Finished.', color='red', attrs=['reverse', 'blink']))
    print('''
         ad88 88             88           88                              88  
        d8"   ""             ""           88                              88  
        88                                88                              88  
        MM88MMM 88 8b,dPPYba,88 ,adPPYba, 88,dPPYba,   ,adPPYba,  ,adPPYb,88  
        88    88 88P'   `"8a 88 I8[    "" 88P'    "8a a8P_____88 a8"    `Y88  
        88    88 88       88 88  `"Y8ba,  88       88 8PP""""""" 8b       88  
        88    88 88       88 88 aa    ]8I 88       88 "8b,   ,aa "8a,   ,d88  
        88    88 88       88 88 `"YbbdP"' 88       88  `"Ybbd8"'  `"8bbdP"Y8  ''')

    input()
    os.system('cls')

exit()

# def input_data():
#     print(info["submask"])
#     subnet_mask = input("Enter a subnet mask (if 0 it'll calculate given n_hosts and subnets): ")
#     print("")
#     n_hosts = input("Enter number of hosts (if 0 it'll create the maximum given number of subnets and mask):")
#     print("")
#     n_subnets = input("Enter number of subnets (if 0 it'll create the maximum given number of hosts and mask):")
#     print("")
#     return check_data(subnet_mask,n_hosts,n_subnets)

# def fill_mask(mask, n_hosts, n_subnets):
#     n_subnet_adresses = n_hosts + 2
#     n_adresses = n_subnet_adresses * n_subnets 
#     n_usable_bits = len(str(bin(n_adresses)))
#     mask = 32-n_usable_bits
#     if not (mask >= 8 and mask <= 30): #limite
#         print("numero de hosts o subnets es erroneo")
#     return mask, n_hosts, n_subnets
# def fill_n_hosts(mask, n_hosts, n_subnets):
#     n_hosts = math.floor((2**(32-mask))/(n_subnets - 2))
#     if (n_hosts < 2): #limite
#         print("numero de subnets o mask es erroneo")
#     return mask, n_hosts, n_subnets
# def fill_n_subnets(mask, n_hosts, n_subnets):
#     print(f"{mask} : {n_hosts} :{str((2**(32-mask))) }: {str((n_hosts+2))}")
#     n_subnets= math.floor((2**(32-mask))/(n_hosts+2))
#     if (n_subnets<1):
#         print("numero de hosts o mask es erroneo")
#     return mask, n_hosts, n_subnets
    
# def check_data(mask, n_hosts, n_subnets):
#     """checks if extra data is correctly"""
#     #checking for errors on imput
#     if not ((mask.isnumeric() and int(mask) >= 8 and int(mask) <= 30) or (mask.isdigit() and int(mask) == 0)): #limite
#         print("subnet mask should be a digit from 8 to 30 or 0")
#     elif not (n_hosts.isnumeric()):
#         print("n_hosts should be numeric")
#     elif not (n_subnets.isnumeric()):
#         print("n_hosts should be a numeric")
#     else:
#         mask = int(mask)
#         n_hosts = int(n_hosts)
#         n_subnets = int(n_subnets)
#         #checking for errors on logic
#         if(mask == 0 and n_subnets != 0 and n_hosts != 0):
#             mask, n_hosts, n_subnets=fill_mask(mask, n_hosts, n_subnets)
#         elif(mask != 0 and n_subnets == 0 and n_hosts != 0):
#             mask, n_hosts, n_subnets=fill_n_subnets(mask, n_hosts, n_subnets)
#         elif(mask != 0 and n_subnets != 0 and n_hosts == 0):
#             mask, n_hosts, n_subnets=fill_n_hosts(mask, n_hosts, n_subnets)
#         elif(mask != 0 and n_subnets != 0 and n_hosts != 0):
#             mask_calculada, n_hosts, n_subnets=fill_mask(mask, n_hosts, n_subnets)
#             if (mask_calculada != mask):
#                 print("Error on input (mask, subnet, hosts)")
#         else:
#             print("Expected at least 2 of inputs (masks/subnets/hosts)")
#         return mask, n_hosts, n_subnets
        
#     raise Exception("something went wrong")


# info = \
# {
# "submask":"Remember a submask can only go up to 30 becase it needs at least 3 hosts\
#      (2 numbers) to exist (number of bits to not use, 1-30)"
# }

# def get_binlist_backward(bin_str, bottom, size=8):
#     ls = []
#     i = len(bin_str)
#     for _ in range(4):
#         if(i-size >= bottom):
#             x = slice(i-size, i, 1)
#             i = i - size
#             print(x)
#             print(bin_str[x])
#             ls.insert(0, bin_str[x])
#         elif(i>bottom):
#             x = slice(bottom, i, 1)
#             print(x)
#             print(bin_str[x])
#             ls.insert(0,bin_str[x])
#             break
#         else:
#             break
#     return ls
# def get_binlist_forward(bin_str, top, size=8):
#     ls = []
#     i = 0
#     for _ in range(4):
#         if(i+size <= top):
#             x = slice(i, i+size, 1)
#             i = i + size
#             print(x)
#             print(bin_str[x])
#             ls.append(bin_str[x])
#         elif(i<top):
#             x = slice(i, top, 1)
#             print(x)
#             print(bin_str[x])
#             ls.append(bin_str[x])
#             break
#         else:
#             break
#     return ls

# def main_handler():
#     ip_address = input("Enter an IP address: ")
#     ip_bytes=check_ip(ip_address)
    

#     mask, n_hosts, n_subnets = input_data()

    
#     ip_bytes_bin = [str(bin(int(i))[2:].zfill(8)) for i in ip_bytes]
#     ip_adress_bin_str = ""
#     for byte in ip_bytes_bin:
#         ip_adress_bin_str = ip_adress_bin_str+byte
#     print(ip_adress_bin_str)    
#     network_id = ip_adress_bin_str[0: mask+1] #this wont change
#     subnet_adress = ip_adress_bin_str[mask+1:]
#     subnet_adress2 = get_binlist_backward(ip_adress_bin_str,mask)

#     subnet_adress = int(subnet_adress, 2) 

#     result = "id, Subnet Address, Host Adress Range, Broadcast\n"
#     for subnet_id in range(n_subnets):
#         subnet_add = str(network_id)+str(subnet_adress)
#         firt_host = str(network_id)+bin(subnet_adress + n_hosts+1)[2:]
#         last_host =  str(network_id)+bin(subnet_adress + n_hosts+1)[2:]
#         host_add_range =  firt_host+ ":"+ last_host
#         broadcast = str(network_id)+bin(subnet_adress + n_hosts+2)[2:]  
#         result = result + f"{subnet_id},{subnet_add},{host_add_range},{broadcast}" 
#         result = result+"\n"
#         subnet_adress = subnet_adress + n_hosts+3
#     print(result)




# main_handler()