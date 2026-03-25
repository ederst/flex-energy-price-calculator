from datetime import date
from pathlib import Path
from statistics import StatisticsError

from .models.registry import get_model, get_metadata, list_models


def generate_monthly_report(
    target_month: date,
    output_dir: Path,
    include_details: bool = True,
) -> Path:
    models = list_models()
    month_name = target_month.strftime("%B %Y")

    report_lines = [
        f"# Energy Price Report: {month_name}",
        "",
        f"**Generated:** {date.today().isoformat()}",
        "",
        "## Summary",
        "",
        "| Model | Net (ct/kWh) | Gross (ct/kWh) |",
        "|-------|--------------|-----------------|",
    ]

    model_calcs = []
    for model_name in models:
        model_cls = get_model(model_name)
        try:
            calc = model_cls(target_month)
        except StatisticsError:
            continue
        if not calc.prices:
            continue
        meta = get_metadata(model_name)
        model_calcs.append((model_name, calc, meta))
        report_lines.append(
            f"| [{model_name}](#{model_name}) | {calc.net_price:.2f} | {calc.gross_price:.2f} |"
        )

    if not model_calcs:
        report_lines.append("| _No data available_ | - | - |")

    if include_details:
        report_lines.extend([
            "",
            "## Details",
            "",
        ])

        for model_name, calc, meta in model_calcs:
            report_lines.extend([
                f"### {model_name}",
                "",
                f"**Description:** {meta.description}",
                f"**Fees:** {meta.fees} €/month",
                f"**Prices used:** {len(calc.prices)} days",
                f"**Skipped days:** {len(calc.skipped_days)}",
                "",
                "| Date | Price (€/MWh) |",
                "|-------|----------------|",
            ])

            for price_date, price_value in calc.prices:
                report_lines.append(f"| {price_date} | {price_value:.2f} |")

            if calc.skipped_days:
                report_lines.extend([
                    "",
                    f"**Skipped:** {', '.join(str(d) for d in sorted(calc.skipped_days))}",
                ])

            report_lines.extend([
                "",
                f"**Avg stock price:** {calc.average_price:.2f} €/MWh",
                "",
            ])

    year_str = target_month.strftime("%Y")
    month_file = target_month.strftime("%m")
    year_dir = output_dir / year_str
    year_dir.mkdir(parents=True, exist_ok=True)

    report_file = year_dir / f"{month_file}.md"
    report_file.write_text("\n".join(report_lines))

    return report_file


def update_index(output_dir: Path) -> None:
    index_lines = [
        "# Energy Price Reports",
        "",
        "This page is automatically updated daily.",
        "",
        "## Reports",
        "",
    ]

    year_dirs = sorted(output_dir.glob("*"), reverse=True)
    for year_dir in year_dirs:
        if not year_dir.is_dir() or year_dir.name.startswith("."):
            continue

        index_lines.append(f"### {year_dir.name}")
        index_lines.append("")

        month_files = sorted(year_dir.glob("*.md"), reverse=True)
        for month_file in month_files:
            report_content = month_file.read_text()
            first_line = report_content.split("\n")[0]
            title = first_line.lstrip("# ").strip()

            index_lines.append(f"- [{title}]({year_dir.name}/{month_file.name})")

        index_lines.append("")

    index_file = output_dir / "index.md"
    index_file.write_text("\n".join(index_lines))
