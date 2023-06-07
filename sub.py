#!/usr/bin/env python3
# Subnet Calculator by Justin Ackermann
# GLN LF 08

import argparse, re, math, sys, os, json, util

log_file = 'logs/subnet_logger.log'
scriptroot = os.path.dirname(os.path.abspath(__file__))

def _ip_to_bin(input: str) -> str:                                           # input z.B. : 192.168.10.10   output: 11000000101010000000101000001010
    return ''.join([bin(int(elem))[2:].zfill(8) for elem in input.split('.')])

def _bin_to_ip(input: str) -> str:                                           # input z.B. : 11000000101010000000101000001010     output: 192.168.10.10  
    return '.'.join([str(int(input[i:i+8], 2)) for i in range(0, len(input), 8)])

def _calculate_subnet(ip: str, cidr: int, num_subnets: int) -> dict:
    try:
        needed_bits = int(math.ceil(math.log(num_subnets, 2)))                  # Log to base two gives the amount of needed extra bits. We have to round it up to full numbers.
        new_cidr = cidr + needed_bits  
        old_subnet_mask = '1' * cidr + '0' * (32 - cidr)                        
        new_subnet_mask = '1' * new_cidr + '0' * (32 - new_cidr)                    
        remaining_bits = 32 - new_cidr 
        
        net, nets_dict, step  =  0, {}, 2 ** remaining_bits                     # Step size is free Hostbits to the power of 2
        for i in range(num_subnets):
            netid_bin = ip[:cidr] + str(bin(net)[2:]).zfill(32 - cidr)          # first part of ip (set hostbits) + step size converted to binary and filled to remaining bits
            broadcast = netid_bin[:new_cidr] + '1' * remaining_bits             # Fill ip string with 1's after cutting ip addr at set hostbits
            first_host = netid_bin[:new_cidr] + '0' * (remaining_bits - 1) + '1'# Fill ip string with 0's after cuttng ip addr at set hostbits (net id)
            last_host = broadcast[:-1] + '0'                                    # Take broadcast addr except last bit and add '0' to end (1 host less than broadcast)

            nets_dict |= {f'{i}': {'id': _bin_to_ip(netid_bin), 'broadcast': _bin_to_ip(broadcast), 'first_host': _bin_to_ip(first_host), 'last_host': _bin_to_ip(last_host)}}  # Append result to dict and convert binary strings into ip adresses
            net += step
        subnet_info = {'old_mask': _bin_to_ip(old_subnet_mask), 'new_mask': _bin_to_ip(new_subnet_mask), 'new_cidr': new_cidr, 'ip_adresses': step, 'hosts': (step-2), 'nets': nets_dict }  # Append nets dict to result dict containing additional general infos for all nets
        return subnet_info
    except Exception as e:
        logger.error("_calculate_subnet: " + repr(e) )
        return None

if __name__ == '__main__':
    logger = util.create_logger('subnet_logger', log_file)
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', type=str, required=True, metavar='IP Address/NetID', help='IP Address in decimal dotted notation, e.g. 192.168.10.45')
    parser.add_argument('-m', type=str, required=True, metavar='CIDR', help='Subnet Mask in CIDR notation without slash, e.g. 24')
    parser.add_argument('-n', type=int, required=True, metavar='SubnetNumber', help='The amount of subnets that you want')
    parser.add_argument('-j', type=str, required=False, const='output.json', nargs='?', metavar='JSON Dump', help='Dump result as json file. Specify a filename.')
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)                               # Print help function when no arguments are given
        sys.exit(1)
    args = parser.parse_args()
    valid_ip = "^(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$" 
    valid_cidr = "^(?:[0-9]|[1-2][0-9]|3[0-2])$"
    ip_input, cidr = str(args.i), int(args.m)

    if(re.match(valid_ip, ip_input) and re.match(valid_cidr, str(cidr))) :                                     
        try:
            num_subnets = int(args.n)
            result = _calculate_subnet(ip=_ip_to_bin(ip_input), cidr=cidr, num_subnets=num_subnets)

            if result:
                util.draw_console(util.draw_panel(ip_input, cidr, num_subnets, result))            
                logger.info(f'Calculation of Subnets for {ip_input}/{cidr} with {num_subnets} subnets done:\n{result}\n')
                if args.j:
                    json_filename = args.j
                    with open(f'{scriptroot}/{json_filename}', "w") as json_file:
                        json.dump(result, json_file)
                        logger.info(f'Calculation of Subnets for {ip_input}/{cidr} with {num_subnets} subnets dumped as JSON to {scriptroot}/{json_filename}')
            else:
                raise ValueError("_calculate_subnet returned None. Check if the values you specified are right.")
        except Exception as e:
            print(repr(e))
            logger.error('main: ' + repr(e))
    else:
        print('IP or Subnet Mask did not match pattern. \nFor IP use: 0.0.0.0 till 255.255.255.255\nFor Mask use: 0 till 32')
            
        
    