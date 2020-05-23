"""Simple test to demonstrate an existing alignment bug when
   using some unicode symbols and color."""

from rich.console import Console
from rich.table import Table

console = Console()


def print_table(char, color=False):
    table = Table(show_header=False)
    table.add_column()
    if color:
        table.add_row("[yellow]%s[/yellow]" % char)
    else:
        table.add_row(char)
    console.print(table)


print_table(">", color=False)
print_table("🡢", color=False)
print_table(">", color=True)
print_table("🡢", color=True)
