from datetime import date
from dateutil.relativedelta import relativedelta

import typer

from flex_energy_price_calculator.models.base import DEFAULT_CACHE_DIR
from flex_energy_price_calculator.models.registry import get_model, get_metadata, list_models

import flex_energy_price_calculator.models.oekostrom  # noqa: F401
import flex_energy_price_calculator.models.gogreenenergy  # noqa: F401
import flex_energy_price_calculator.models.noprovider  # noqa: F401
import flex_energy_price_calculator.models.fullmonth  # noqa: F401

app = typer.Typer(help="Flexible Energy Price Calculator")


@app.command()
def main(
    start: str = typer.Option(None, "--start", "-s", help="Start month (YYYY-MM)"),
    end: str = typer.Option(None, "--end", "-e", help="End month (YYYY-MM), defaults to start"),
    model: str = typer.Option(None, "--model", "-m", help="Tariff model name"),
    list_models_flag: bool = typer.Option(False, "--list", "-l", help="List available models"),
):
    if list_models_flag:
        typer.echo("Available models:")
        for name in list_models():
            meta = get_metadata(name)
            if meta:
                typer.echo(f"  {meta.name}: {meta.description} (fees: {meta.fees} €/month)")
        raise typer.Exit()

    if not start or not model:
        raise typer.BadParameter("Both --start and --model are required")

    model_cls = get_model(model)
    if not model_cls:
        available = ", ".join(list_models())
        raise typer.BadParameter(f"Unknown model: {model}\nAvailable models: {available}")

    start_date = date.fromisoformat(f"{start}-01")
    if end:
        end_date = date.fromisoformat(f"{end}-01")
    else:
        end_date = start_date

    typer.echo(f"Calculating prices for {start} to {end or start}\n---")

    DEFAULT_CACHE_DIR.mkdir(exist_ok=True)

    current_date = start_date
    display_model = {
        'prices': [],
        'average_prices': [],
        'status_messages': [],
        'net_prices': [],
        'gross_prices': [],
    }
    while current_date <= end_date:
        calc_model = model_cls(current_date)

        display_model['prices'].extend(calc_model.prices)
        display_model['average_prices'].append(calc_model.average_price)
        display_model['status_messages'].append(calc_model.status_message),
        display_model['net_prices'].append(calc_model.net_price),
        display_model['gross_prices'].append(calc_model.gross_price),
        current_date = current_date + relativedelta(months=1)

    average_price = sum(display_model['average_prices']) / len(display_model['average_prices'])
    net_price = sum(display_model['net_prices']) / len(display_model['net_prices'])
    gross_price = sum(display_model['gross_prices']) / len(display_model['gross_prices'])

    prices_string = "".join([f"\n  - {x[0]}: {x[1]}" for x in display_model['prices']])

    typer.echo(
        (
            f"stock prices: {prices_string}\n"
            f"avg stock price: {average_price:5.2f}€/MWh\n"
            "---\n"
            f"net enduser price:   {net_price:5.2f}ct/KWh\n"
            f"gross enduser price: {gross_price:5.2f}ct/KWh\n"
        )
    )


if __name__ == "__main__":
    app()
