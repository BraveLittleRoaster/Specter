import os.path

import ujson
from rich.table import Table
from rich.console import Console

console = Console()


def render_ja3(test_case, all_ja3):
    # Check if the number of JA3 hashes is greater than 25
    truncated = False
    if len(all_ja3) > 25:
        total_hashes = len(all_ja3)
        all_ja3 = list(all_ja3)[:25]
        truncated = True

    # Create a table with the specified title and columns
    table = Table(title=f"Unique JA3 Hashes: {test_case}", title_justify="center")
    table.add_column("Test Case", justify="center", style="magenta")
    table.add_column("JA3 Hash", justify="center", style="cyan")

    for ja3 in all_ja3:
        table.add_row(test_case, ja3)
    console.print("="*20)
    console.print(table)

    if truncated:
        console.print(f"[bold red]Note:[/] {test_case}: List truncated to the first 25 of {total_hashes} JA3 hashes. The JA3 is likely randomized!")
    console.print("="*20)

def get_unique_ja3(ja3_files):

    for ja3_file in ja3_files:

        test_case = os.path.basename(ja3_file).split("_")[0]

        with open(ja3_file, 'r') as f:
            jq = ujson.loads(f.read())

        all_ja3 = set()
        for _ in jq:
            all_ja3.add(_['ja3_digest'])

        render_ja3(test_case, all_ja3)


def render_ja4h(test_case, ja4_file, all_ja4h):

    ja4h_truncated = False
    if len(all_ja4h) > 25:
        total_hashes = len(all_ja4h)
        all_ja4h = list(all_ja4h)[:25]
        ja4h_truncated = True

    ja4h_table = Table(title=f"Unique JA4H Hashes: {test_case} | {os.path.basename(ja4_file)}", title_justify="center")
    ja4h_table.add_column("Test Case", justify="center", style="magenta")
    ja4h_table.add_column("JA4H Hash", justify="center", style="cyan")

    for ja4h in all_ja4h:
        ja4h_table.add_row(test_case, ja4h)
    console.print("=" * 20)
    console.print(ja4h_table)
    if ja4h_truncated:
        console.print(f"[bold red]Note:[/] {test_case}: List truncated to the first 25 of {total_hashes} JA4 hashes. The JA4H is possibly randomized!")
    console.print("="*20)

def render_ja4(test_case, ja4_file, all_ja4):

    ja4_truncated = False
    if len(all_ja4) > 25:
        total_hashes = len(all_ja4)
        all_ja4 = list(all_ja4)[:25]
        ja4_truncated = True

    ja4_table = Table(title=f"Unique JA4 Hashes: {test_case} | {os.path.basename(ja4_file)}", title_justify="center")
    ja4_table.add_column("Test Case", justify="center", style="magenta")
    ja4_table.add_column("JA4 Hash", justify="center", style="cyan")

    for ja4 in all_ja4:
        ja4_table.add_row(test_case, ja4)

    console.print("=" * 20)
    console.print(ja4_table)
    if ja4_truncated:
        console.print(f"[bold red]Note:[/] {test_case}: List truncated to the first 25 of {total_hashes} JA4 hashes. The JA4 is likely randomized!")
    console.print("="*20)


def get_unique_ja4(ja4_files):

    for ja4_file in ja4_files:
        all_ja4 = set()
        all_ja4h = set()
        with open(ja4_file, 'r') as f:
            jq = ujson.loads(f.read())
        f.close()

        test_case = os.path.basename(ja4_file).split('_')[0]

        for _ in jq:
            ja4 = _.get('JA4')
            if ja4:
                all_ja4.add(ja4)
            ja4h = _.get('JA4H')
            if ja4h:
                all_ja4h.add(ja4h)

        if all_ja4:
            render_ja4(test_case, ja4_file, all_ja4)
        if all_ja4h:
            render_ja4h(test_case, ja4_file, all_ja4h)
