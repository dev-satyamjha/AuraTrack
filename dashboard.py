import time
import requests
import sys
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.console import Console
from rich.align import Align
from rich.text import Text

API_BASE = "http://localhost:8000"
STORE_ID = sys.argv[1] if len(sys.argv) > 1 else "ST1008"

def fetch_data():
    try:
        metrics = requests.get(f"{API_BASE}/metrics/{STORE_ID}", timeout=2).json()
        funnel = requests.get(f"{API_BASE}/funnel/conversion/{STORE_ID}", timeout=2).json()
        return metrics, funnel
    except Exception:
        return None, None

def generate_dashboard():
    metrics, funnel = fetch_data()

    if not metrics or not funnel or "error" in funnel:
        return Panel(
            Text("⚠️ API Offline or POS data missing. Ensure FastAPI is running.", style="bold red", justify="center"),
            title="AuraTrack Live"
        )

    kpi_table = Table(show_header=True, header_style="bold magenta", expand=True)
    kpi_table.add_column("Unique Visitors", justify="center")
    kpi_table.add_column("Avg Dwell (sec)", justify="center")
    kpi_table.add_column("Abandonment Rate", justify="center")
    kpi_table.add_column("Conversion Rate", justify="center")

    kpi_table.add_row(
        str(metrics.get("unique_visitors_today", 0)),
        str(metrics.get("avg_dwell_seconds", 0)),
        f"{metrics.get('queue_abandonment_rate', 0.0)}%",
        f"{funnel.get('conversion_rate_percentage', 0.0)}%"
    )

    funnel_table = Table(show_header=True, header_style="bold cyan", expand=True)
    funnel_table.add_column("Funnel Stage", justify="left")
    funnel_table.add_column("Count", justify="right")

    funnel_table.add_row("Billing Queue Completions", str(funnel.get("total_queue_completions", 0)))
    funnel_table.add_row("Matched POS Transactions", str(funnel.get("matched_transactions", 0)))

    layout = Layout()
    layout.split_column(
        Layout(Panel(Align.center(Text("🛍️  AuraTrack Intelligence Engine", style="bold green")), border_style="green"), size=3),
        Layout(Panel(kpi_table, title="📊 Real-Time Store Performance", border_style="blue"), size=6),
        Layout(Panel(funnel_table, title="🎯 Point of Sale Correlation", border_style="cyan"))
    )
    return layout

if __name__ == "__main__":
    console = Console()
    console.clear()

    with Live(generate_dashboard(), refresh_per_second=2, screen=True) as live:
        while True:
            time.sleep(0.5)
            live.update(generate_dashboard())
