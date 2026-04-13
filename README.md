# FortiGate-Policy-Parser

# README.md

## FortiGate Policy TXT to CSV Parser

This script parses FortiGate firewall policy configuration text from a `.txt` file and exports the extracted policy values to a CSV file.

## Overview

The script is designed to:

- Read a FortiGate policy configuration saved as a plain text file
- Start parsing at `config firewall policy`
- Stop parsing at `end`
- Process each firewall policy block beginning with `edit`
- Finish each policy block at `next`
- Extract relevant `set` values
- Export the parsed results into a CSV file

## Input Requirements

Before running the script, ensure the FortiGate policy file:

- Is saved as a `.txt` file
- Contains firewall policy configuration in FortiGate CLI format
- Includes the section:
  - `config firewall policy`
  - one or more `edit ... next` policy blocks
  - closing `end`

## Expected Format

The script expects input similar to the following:

```text
config firewall policy
    edit 123
        set uuid af3f57d0-a25e-51f0-e285-6666b9984125
        set srcintf "port1"
        set dstintf "port2"
        set action accept
        set srcaddr "10.167.1.12" "AD_192.168.1.14" "NET_10.183.1.10-17"
        set dstaddr "NET_10.133.24.0/28" "NET_10.133.24.16/28" "NET_10.133.24.32/28"
        set schedule "always"
        set service "DNS" "PING" "NTP"
        set logtraffic all
    next
end
```

## How It Works

The script processes the configuration using the following logic:

1. Locate the line `config firewall policy`
2. Begin reading policy entries
3. Detect each policy block starting with `edit`
4. Capture values from `set` statements inside the block
5. End the current policy when `next` is reached
6. Stop parsing when `end` is reached
7. Write all collected policy data to a CSV file

## Output

The script exports the parsed firewall policy data into a CSV file.

Typical values that may be captured include:

- Policy ID
- UUID
- Source interface
- Destination interface
- Action
- Source address objects
- Destination address objects
- Schedule
- Services
- Log traffic setting

## Notes

- The input file must be properly formatted for the parser to work correctly.
- Multi-value fields such as `srcaddr`, `dstaddr`, and `service` should remain on a single line if the script expects line-based parsing.
- Parsing begins only at `config firewall policy`.
- Parsing stops at the first `end`.

## Example Use Case

Use this script when you need to:

- Convert FortiGate firewall policies into CSV format
- Review policies in spreadsheet software
- Perform reporting or auditing on exported policy data
- Simplify analysis of FortiGate policy configurations

## Limitations

Depending on the implementation, the script may assume:

- One complete firewall policy section per file
- Standard FortiGate CLI formatting
- No malformed or incomplete policy blocks
- Values are structured using `set <field> <value>`

## Suggested File Structure

```text
project/
├── parser.py
├── policies.txt
└── output.csv
```

## Running the Script

Example:

```bash
python parser.py
```

If your script accepts file arguments, you may use something like:

```bash
python parser.py policies.txt output.csv
```

## Summary

This script provides a simple way to extract FortiGate firewall policy entries from a text configuration file and convert them into a CSV format for easier review and analysis.
