# Utility Module
# This module handles the logging and representation of the calculator output in the terminal

import logging, os
from rich.console import Console, Group
from rich.table import Table
from rich.panel import Panel
from rich.align import Align

scriptroot = os.path.dirname(os.path.abspath(__file__))

def create_logger(loggername, filepath) -> logging.Logger:
    # Create and return the Logger object
    logger = logging.getLogger(loggername); logger.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler(f'{scriptroot}/{filepath}'); file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter); logger.addHandler(file_handler)
    return logger

def draw_panel(ip: str, cidr: int, num_subnets: int, result: dict) -> Panel:
    # Draw a neat panel showing the output information
    info_table = Table(show_header=False, border_style='blue',box=None)
    info_table.add_column("Info", justify="left", style='blue')
    info_table.add_column("Value", justify="left")
    info_table.add_row('\n','\n')
    info_table.add_row("Input IP:", f"{ip}/{cidr}")
    info_table.add_row("Subnet Mask Decimal:", result['old_mask'])
    info_table.add_row("Number of Subnets:", str(num_subnets))

    info_table.add_row('\n')
    info_table.add_row("New Mask:", result["new_mask"])
    info_table.add_row("Number of IP Adresses:", str(result['ip_adresses']))
    info_table.add_row("Number of adressable hosts:", str(result['hosts']))
    info_table.add_row('\n','\n')
    
    table = Table(border_style='blue', header_style='bold blue')
    table.add_column("Net", style='bold blue', justify='center')
    table.add_column("ID")
    table.add_column("First Host")
    table.add_column("Last Host")
    table.add_column("Broadcast")
    
    new_cidr = result['new_cidr']
    for i in range(0, len(result['nets'])):
        info = result['nets'][f'{i}']
        table.add_row(str(i), f"{info['id']} /{new_cidr}", info['first_host'],info['last_host'], info['broadcast'])
    
    panel = Panel(Align(Group(Align(info_table,align='center'),table), align='center'), title="🔥 » Subnetzrechner « 🔥", border_style='blue')
    return panel

def draw_console(panel: Panel):
    # Creates a console object and prints the panel defined earlier
    console = Console()
    return console.print(panel)
