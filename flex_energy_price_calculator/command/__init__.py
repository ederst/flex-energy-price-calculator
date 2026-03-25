from datetime import date
from dateutil.relativedelta import relativedelta

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from flex_energy_price_calculator.models.base import DEFAULT_CACHE_DIR
from flex_energy_price_calculator.models.registry import get_model, get_metadata, list_models

import flex_energy_price_calculator.models.oekostrom  # noqa: F401
import flex_energy_price_calculator.models.gogreenenergy  # noqa: F401
import flex_energy_price_calculator.models.noprovider  # noqa: F401
import flex_energy_price_calculator.models.fullmonth  # noqa: F401

app = typer.Typer(help="Flexible Energy Price Calculator")
console = Console()


@app.command()
def main(
    start: str = typer.Option(None, "--start", "-s", help="Start month (YYYY-MM)"),
    end: str = typer.Option(None, "--end", "-e", help="End month (YYYY-MM), defaults to start"),
    model: str = typer.Option(None, "--model", "-m", help="Tariff model name"),
    list_models_flag: bool = typer.Option(False, "--list", "-l", help="List available models"),
):
    if list_models_flag:
        console.print("\n[bold]Available tariff models:[/bold]\n")
        for name in list_models():
            meta = get_metadata(name)
            if meta:
                console.print(f"  [cyan]{meta.name}[/cyan]  {meta.description}")
                console.print(f"          fees: [yellow]{meta.fees} €/month[/yellow]")
        console.print()
        raise typer.Exit()

    if not start or not model:
        raise typer.BadParameter("Both --start and --model are required")

    model_cls = get_model(model)
    if not model_cls:
        available = ", ".join(list_models())
        raise typer.BadParameter(f"Unknown model: {model}\nAvailable models: {available}")

    meta = get_metadata(model)
    if not meta:
        raise typer.BadParameter(f"Could not retrieve metadata for model: {model}")

    start_date = date.fromisoformat(f"{start}-01")
    if end:
        end_date = date.fromisoformat(f"{end}-01")
    else:
        end_date = start_date

    console.print(f"\n[bold]Calculating prices for[/bold] {start} [bold]to[/bold] {end or start}\n")

    DEFAULT_CACHE_DIR.mkdir(exist_ok=True)

    current_date = start_date
    monthly_models = []
    display_model = {
        'prices': [],
        'average_prices': [],
        'status_messages': [],
        'net_prices': [],
        'gross_prices': [],
    }
    while current_date <= end_date:
        calc_model = model_cls(current_date)
        monthly_models.append(calc_model)

        display_model['prices'].extend(calc_model.prices)
        display_model['average_prices'].append(calc_model.average_price)
        display_model['status_messages'].append(calc_model.status_message),
        display_model['net_prices'].append(calc_model.net_price),
        display_model['gross_prices'].append(calc_model.gross_price),
        current_date = current_date + relativedelta(months=1)

    average_price = sum(display_model['average_prices']) / len(display_model['average_prices'])
    net_price = sum(display_model['net_prices']) / len(display_model['net_prices'])
    gross_price = sum(display_model['gross_prices']) / len(display_model['gross_prices'])

    console.print(Panel.fit(
        f"[bold cyan]Model:[/bold cyan] {meta.name}\n"
        f"[bold cyan]Description:[/bold cyan] {meta.description}\n"
        f"[bold cyan]Fees:[/bold cyan] {meta.fees} €/month",
        title="[bold]Tariff Info[/bold]",
        border_style="cyan",
    ))

    price_table = Table(title="\n[bold]Stock Prices[/bold]", show_header=True, header_style="bold magenta")
    price_table.add_column("Date", style="white", justify="left")
    price_table.add_column("Price (€/MWh)", style="yellow", justify="right")

    for price_date, price_value in display_model['prices']:
        price_table.add_row(str(price_date), f"{price_value:.2f}")

    console.print(price_table)

    all_skipped = []
    for m in monthly_models:
        all_skipped.extend(m.skipped_days)
    if all_skipped:
        skipped_str = "\n".join(str(d) for d in sorted(all_skipped))
        console.print(Panel.fit(
            f"[yellow]{skipped_str}[/yellow]",
            title="[bold yellow]⚠ Skipped Days (no data)[/bold yellow]",
            border_style="yellow",
        ))

    results_table = Table(show_header=False, box=None, padding=(0, 2))
    results_table.add_column("Label", style="white")
    results_table.add_column("Value", style="bold green", justify="right")

    results_table.add_row("[bold]Avg Stock Price[/bold]", f"{average_price:.2f} €/MWh")
    results_table.add_row("[bold]Net Enduser Price[/bold]", f"{net_price:.2f} ct/kWh")
    results_table.add_row("[bold]Gross Enduser Price[/bold]", f"{gross_price:.2f} ct/kWh")

    console.print(Panel.fit(
        results_table,
        title="[bold]Results[/bold]",
        border_style="green",
    ))
    console.print()


if __name__ == "__main__":
    app()
