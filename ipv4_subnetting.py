from dataclasses import dataclass
from typing import Tuple
import re

ip = None
subnet_quantity = None
network_quantity = None


import math 

def check_ip(ip_address):
    '''
    Checks the adress has the correct format and isnt impossible.
    returns: array of each byte
    '''
    ip_bytes = ip_address.split('.')
    if len(ip_bytes) < 4:
        raise Exception("Wrong format, please enter ip adress as the example: 128.0.0.0") 
    for byte in ip_bytes:
        if byte.isdigit():
            if int(byte) > 255 or int(byte) < 0:
                raise Exception(f" byte {byte} should be between 0 and 255")
        else:
            raise Exception(f"numero {byte} invalido")
    return(ip_bytes)

def input_data():
    print(info["submask"])
    subnet_mask = input("Enter a subnet mask (if 0 it'll calculate given n_hosts and subnets): ")
    print("")
    n_hosts = input("Enter number of hosts (if 0 it'll create the maximum given number of subnets and mask):")
    print("")
    n_subnets = input("Enter number of subnets (if 0 it'll create the maximum given number of hosts and mask):")
    print("")
    return check_data(subnet_mask,n_hosts,n_subnets)

def fill_mask(mask, n_hosts, n_subnets):
    n_subnet_adresses = n_hosts + 2
    n_adresses = n_subnet_adresses * n_subnets 
    n_usable_bits = len(str(bin(n_adresses)))
    mask = 32-n_usable_bits
    if not (mask >= 8 and mask <= 30): #limite
        print("numero de hosts o subnets es erroneo")
    return mask, n_hosts, n_subnets
def fill_n_hosts(mask, n_hosts, n_subnets):
    n_hosts = math.floor((2**(32-mask))/(n_subnets - 2))
    if (n_hosts < 2): #limite
        print("numero de subnets o mask es erroneo")
    return mask, n_hosts, n_subnets
def fill_n_subnets(mask, n_hosts, n_subnets):
    print(f"{mask} : {n_hosts} :{str((2**(32-mask))) }: {str((n_hosts+2))}")
    n_subnets= math.floor((2**(32-mask))/(n_hosts+2))
    if (n_subnets<1):
        print("numero de hosts o mask es erroneo")
    return mask, n_hosts, n_subnets
    
def check_data(mask, n_hosts, n_subnets):
    """checks if extra data is correctly"""
    #checking for errors on imput
    if not ((mask.isnumeric() and int(mask) >= 8 and int(mask) <= 30) or (mask.isdigit() and int(mask) == 0)): #limite
        print("subnet mask should be a digit from 8 to 30 or 0")
    elif not (n_hosts.isnumeric()):
        print("n_hosts should be numeric")
    elif not (n_subnets.isnumeric()):
        print("n_hosts should be a numeric")
    else:
        mask = int(mask)
        n_hosts = int(n_hosts)
        n_subnets = int(n_subnets)
        #checking for errors on logic
        if(mask == 0 and n_subnets != 0 and n_hosts != 0):
            mask, n_hosts, n_subnets=fill_mask(mask, n_hosts, n_subnets)
        elif(mask != 0 and n_subnets == 0 and n_hosts != 0):
            mask, n_hosts, n_subnets=fill_n_subnets(mask, n_hosts, n_subnets)
        elif(mask != 0 and n_subnets != 0 and n_hosts == 0):
            mask, n_hosts, n_subnets=fill_n_hosts(mask, n_hosts, n_subnets)
        elif(mask != 0 and n_subnets != 0 and n_hosts != 0):
            mask_calculada, n_hosts, n_subnets=fill_mask(mask, n_hosts, n_subnets)
            if (mask_calculada != mask):
                print("Error on input (mask, subnet, hosts)")
        else:
            print("Expected at least 2 of inputs (masks/subnets/hosts)")
        return mask, n_hosts, n_subnets
        
    raise Exception("something went wrong")


info = \
{
"submask":"Remember a submask can only go up to 30 becase it needs at least 3 ports\
     (2 numbers) to exist (number of bits to not use, 1-30)"
}

def get_binlist_backward(bin_str, bottom, size=8):
    ls = []
    i = len(bin_str)
    for _ in range(4):
        if(i-size >= bottom):
            x = slice(i-size, i, 1)
            i = i - size
            print(x)
            print(bin_str[x])
            ls.insert(0, bin_str[x])
        elif(i>bottom):
            x = slice(bottom, i, 1)
            print(x)
            print(bin_str[x])
            ls.insert(0,bin_str[x])
            break
        else:
            break
    return ls
def get_binlist_forward(bin_str, top, size=8):
    ls = []
    i = 0
    for _ in range(4):
        if(i+size <= top):
            x = slice(i, i+size, 1)
            i = i + size
            print(x)
            print(bin_str[x])
            ls.append(bin_str[x])
        elif(i<top):
            x = slice(i, top, 1)
            print(x)
            print(bin_str[x])
            ls.append(bin_str[x])
            break
        else:
            break
    return ls

def main_handler():
    ip_address = input("Enter an IP address: ")
    ip_bytes=check_ip(ip_address)
    

    mask, n_hosts, n_subnets = input_data()

    
    ip_bytes_bin = [str(bin(int(i))[2:].zfill(8)) for i in ip_bytes]
    ip_adress_bin_str = ""
    for byte in ip_bytes_bin:
        ip_adress_bin_str = ip_adress_bin_str+byte
    print(ip_adress_bin_str)    
    network_id = ip_adress_bin_str[0: mask+1] #this wont change
    subnet_adress = ip_adress_bin_str[mask+1:]
    subnet_adress2 = get_binlist_backward(ip_adress_bin_str,mask)

    subnet_adress = int(subnet_adress, 2) 

    result = "id, Subnet Address, Host Adress Range, Broadcast\n"
    for subnet_id in range(n_subnets):
        subnet_add = str(network_id)+str(subnet_adress)
        firt_host = str(network_id)+bin(subnet_adress + n_hosts+1)[2:]
        last_host =  str(network_id)+bin(subnet_adress + n_hosts+1)[2:]
        host_add_range =  firt_host+ ":"+ last_host
        broadcast = str(network_id)+bin(subnet_adress + n_hosts+2)[2:]  
        result = result + f"{subnet_id},{subnet_add},{host_add_range},{broadcast}" 
        result = result+"\n"
        subnet_adress = subnet_adress + n_hosts+3
    print(result)




main_handler()