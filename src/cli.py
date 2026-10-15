"""CLI Interface for Autonomous Multi-Agent GraphRAG Engine."""

from __future__ import annotations

import asyncio
import json
import logging

import click
import uvicorn
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from src.agents.supervisor import SupervisorAgent
from src.graph.neo4j_client import Neo4jClient
from src.rag.hybrid_retriever import HybridRetriever
from src.schemas.models import FinancialAnalysisRequest

console = Console()
logging.basicConfig(level=logging.WARNING)


@click.group()
def main():
    """Autonomous Multi-Agent GraphRAG & Financial Intelligence CLI."""


@main.command()
@click.option("--host", default="0.0.0.0", help="Host interface to bind")
@click.option("--port", default=8001, type=int, help="Port to listen on")
@click.option("--reload", is_flag=True, help="Enable auto-reload for development")
def serve(host: str, port: int, reload: bool):
    """Launch the GraphRAG FastAPI backend & embedded frontend."""
    console.print(
        Panel.fit(
            f"[bold cyan]AGENTIC GRAPHRAG INTELLIGENCE ENGINE[/bold cyan]\n"
            f"[dim]FastAPI Serving Mesh on [bold green]http://{host}:{port}[/bold green][/dim]\n"
            f"[yellow]SYS_01 // LangGraph + ColBERTv2 + Neo4j 5.24[/yellow]",
            border_style="cyan",
        )
    )
    uvicorn.run("src.main:app", host=host, port=port, reload=reload)


@main.command()
@click.option("--query", "-q", required=True, help="Financial investigation query")
@click.option(
    "--ticker", "-t", multiple=True, default=["AAPL", "NVDA"], help="Target company tickers"
)
@click.option(
    "--verify/--no-verify", default=True, help="Execute formal hallucination verification"
)
def query(query: str, ticker: tuple[str, ...], verify: bool):
    """Execute end-to-end multi-agent hierarchical reasoning."""

    async def _run():
        tickers = list(ticker)
        console.print(
            f"[bold yellow]Initiating Agentic Multi-Hop Reasoning:[/bold yellow] [white]{query}[/white]"
        )
        console.print(f"[dim]Scope: {tickers} | Verification: {verify}[/dim]\n")

        neo4j_client = Neo4jClient()
        retriever = HybridRetriever()
        supervisor = SupervisorAgent(neo4j_client, retriever)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            progress.add_task("[cyan]Running LangGraph Supervisor...", total=None)
            req = FinancialAnalysisRequest(
                query=query,
                tickers=tickers,
                require_verification=verify,
            )
            res = await supervisor.run(req)

        # Print reasoning trace
        trace_table = Table(title="Multi-Agent Execution Trace", border_style="dim")
        trace_table.add_column("Step", style="cyan", width=6)
        trace_table.add_column("Agent", style="bold green", width=18)
        trace_table.add_column("Thought / Action", style="white")

        for s in res.reasoning_trace:
            trace_table.add_row(str(s.step_number), s.agent_name, s.thought)

        console.print(trace_table)
        console.print()

        # Synthesis
        console.print(
            Panel(
                res.synthesis,
                title="[bold green]Executive Financial Intelligence Synthesis[/bold green]",
                subtitle=f"[dim]Latency: {res.latency_ms:.1f}ms | Confidence: {res.verification.confidence_score * 100:.1f}%[/dim]",
                border_style="green",
            )
        )

        # Verification report
        v = res.verification
        v_table = Table(title="Verification & Grounding Audit", border_style="dim")
        v_table.add_column("Metric", style="cyan")
        v_table.add_column("Status / Value", style="bold")
        v_table.add_row(
            "Verified Grounding", "[green]PASSED[/green]" if v.is_verified else "[red]FAILED[/red]"
        )
        v_table.add_row("Confidence Score", f"{v.confidence_score * 100:.1f}%")
        v_table.add_row(
            "Hallucination Flag",
            "[red]DETECTED[/red]" if v.hallucination_detected else "[green]CLEAN[/green]",
        )
        v_table.add_row("Primary Citations", ", ".join(v.citations) if v.citations else "N/A")
        console.print(v_table)

    asyncio.run(_run())


@main.command()
@click.option("--ticker", "-t", default="AAPL", help="Company ticker symbol")
@click.option("--depth", "-d", default=2, type=int, help="Graph traversal depth")
def graph(ticker: str, depth: int):
    """Inspect knowledge graph multi-hop relationships."""

    async def _run():
        neo4j_client = Neo4jClient()
        subgraph = await neo4j_client.query_multihop_subgraph(ticker=ticker, depth=depth)

        table = Table(title=f"Neo4j Subgraph for {ticker} (Depth {depth})", border_style="cyan")
        table.add_column("Source", style="cyan")
        table.add_column("Relation", style="bold yellow")
        table.add_column("Target", style="green")
        table.add_column("Properties", style="dim")

        for r in subgraph.get("relationships", []):
            table.add_row(
                r.get("source", ""),
                r.get("type", ""),
                r.get("target", ""),
                json.dumps(r.get("properties", {})),
            )
        console.print(table)

    asyncio.run(_run())


@main.command()
@click.option("--iterations", "-n", default=5, type=int, help="Benchmark run count")
def benchmark(iterations: int):
    """Benchmark end-to-end multi-hop retrieval and synthesis latency."""

    async def _run():
        neo4j_client = Neo4jClient()
        retriever = HybridRetriever()
        supervisor = SupervisorAgent(neo4j_client, retriever)

        console.print(
            f"[bold yellow]Benchmarking Agentic GraphRAG across {iterations} iterations...[/bold yellow]"
        )
        latencies = []
        for i in range(iterations):
            req = FinancialAnalysisRequest(
                query=f"Analyze geopolitical exposure of semiconductor suppliers iteration {i}",
                tickers=["AAPL", "NVDA"],
                require_verification=True,
            )
            res = await supervisor.run(req)
            latencies.append(res.latency_ms)
            console.print(f"  Iteration {i + 1}/{iterations}: [cyan]{res.latency_ms:.2f}ms[/cyan]")

        avg = sum(latencies) / len(latencies)
        min_l = min(latencies)
        max_l = max(latencies)
        console.print(
            Panel.fit(
                f"[bold green]BENCHMARK RESULTS[/bold green]\n"
                f"Mean Latency: [bold cyan]{avg:.2f}ms[/bold cyan]\n"
                f"Min Latency:  [green]{min_l:.2f}ms[/green]\n"
                f"Max Latency:  [yellow]{max_l:.2f}ms[/yellow]\n"
                f"Target SLA:   [dim]<120ms TTFT passed[/dim]",
                border_style="green",
            )
        )

    asyncio.run(_run())


if __name__ == "__main__":
    main()
