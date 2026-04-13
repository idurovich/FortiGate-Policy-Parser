# ====================== Instructions ======================
# FortiGate firewall policy extractor → CSV with Excel-friendly formatting
# Supports both quoted and unquoted set values (e.g. set action accept)

import re
import csv
from pathlib import Path
import tkinter as tk
from tkinter import filedialog


def clean_field_values(value_str: str, key: str = None):
    """Extract values - handles both quoted and unquoted values."""
    quoted_values = re.findall(r'"([^"]*)"', value_str)
    if quoted_values:
        return quoted_values

    # No quotes → take the whole remaining text as one value
    value = value_str.strip()
    value = re.split(r'\s+#', value)[0].strip()   # remove inline comments if any
    return [value] if value else []


def parse_fortigate_policies(config_text: str):
    policies = []
    current_policy = None
    in_policy_section = False
    
    lines = config_text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        if not line or line.startswith('#'):
            i += 1
            continue
            
        if line.startswith('config firewall policy'):
            in_policy_section = True
            i += 1
            continue
        elif line == 'end' and in_policy_section:
            if current_policy:
                policies.append(current_policy)
            break
        
        if not in_policy_section:
            i += 1
            continue
        
        if line.startswith('edit '):
            if current_policy:
                policies.append(current_policy)
            try:
                policy_id = int(line.split(maxsplit=1)[1])
                current_policy = {'id': policy_id}
            except (IndexError, ValueError):
                current_policy = {'id': None}
            i += 1
            continue
        
        if line.startswith('set ') and current_policy is not None:
            match = re.match(r'set\s+(\S+)\s+(.*)', line)
            if match:
                key = match.group(1)
                value_str = match.group(2).strip()
                
                # Collect continuation lines if the set value spans multiple lines
                i += 1
                while i < len(lines):
                    next_line = lines[i].strip()
                    if (next_line.startswith(('set ', 'edit ', 'next', 'config ', 'end'))):
                        break
                    if next_line:
                        value_str += ' ' + next_line
                    i += 1
                
                values = clean_field_values(value_str, key)
                
                if not values:
                    current_policy[key] = ''
                elif len(values) == 1:
                    current_policy[key] = values[0]
                else:
                    # Fields that should stay in one line
                    if key in ('name', 'comments', 'logtraffic', 'schedule', 'status'):
                        current_policy[key] = ' '.join(values)
                    else:
                        current_policy[key] = '\n'.join(values)   # multi-line for addresses/services
                
                continue   # important: skip the outer i += 1
        
        i += 1
    
    if current_policy:
        policies.append(current_policy)
    
    return policies


# ====================== File Selection ======================
root = tk.Tk()
root.withdraw()

input_file = filedialog.askopenfilename(
    title="Select FortiGate Configuration File",
    initialdir=r"C:\Users\Acme\Downloads",
    filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
)

if not input_file:
    print("❌ No input file selected.")
    root.destroy()
    exit()

file_path = Path(input_file)

default_output = file_path.parent / f"{file_path.stem}_policies.csv"

output_file = filedialog.asksaveasfilename(
    title="Save Policies as CSV",
    initialdir=str(file_path.parent),
    initialfile=default_output.name,
    defaultextension=".csv",
    filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
)

if not output_file:
    print("❌ No output file selected.")
    root.destroy()
    exit()

output_file = Path(output_file)

# ====================== Processing ======================
try:
    with file_path.open('r', encoding='utf-8') as f:
        config = f.read()

    policies = parse_fortigate_policies(config)

    if not policies:
        print("No firewall policies found.")
    else:
        print(f"✅ Successfully parsed {len(policies)} policies.\n")

        # Extended column list with more useful fields
        desired_columns = [
            'id', 'action', 'name',
            'srcintf', 'srcaddr',
            'dstintf', 'dstaddr',
            'service', 'schedule',
            'comments', 'status', 'uuid',
            'nat', 'ippool', 'poolname',
            'ssl-ssh-profile', 'av-profile', 'ips-sensor', 'webfilter-profile',
            'application-list', 'dlp-sensor', 'emailfilter-profile',
            'utm-status', 'logtraffic', 'inspection-mode'
        ]

        rows = [{col: p.get(col, '') for col in desired_columns} for p in policies]

        # Write CSV with Excel-friendly settings
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=desired_columns)
            writer.writeheader()
            writer.writerows(rows)

        print(f"✅ Policies exported to: {output_file}")
        print("   Tip: Open the CSV in Microsoft Excel for best multi-line display.")

except Exception as e:
    print(f"❌ Error: {e}")

finally:
    root.destroy()
