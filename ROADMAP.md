# Backtester pipeline & roadmap

```mermaid
flowchart TD
    subgraph sources[Data Sources]
        DS[Polymarket CLOB + Gamma API]
    end

    subgraph strats[Strategies]
        ST[Momentum + Mean Reversion]
    end

    DS --> DH
    ST --> BE

    DH[Data Handler<br/>CSV price history] --> BE
    BE[Backtest Engine<br/>Event queue + dispatch] -- signal --> PF
    PF[Portfolio<br/>Not built yet] -- order --> EX
    EX[Execution<br/>Market fill + fee sim] -- fill --> PF
    PF -- equity --> PM[Performance<br/>Not built yet]

    classDef built fill:#eef7ee,stroke:#2f9e44,stroke-width:2px;
    classDef todo fill:#f4f4f5,stroke:#9e9ea7,stroke-width:2px,stroke-dasharray: 5 5;

    class DH,BE,EX built;
    class PF,PM todo;
```

**Legend**: solid green = built and verified. Dashed grey = not built yet.

## Backlog

- Live/continuously-updating data source (currently CSV snapshots only)
- Market resolver ("ask an agent what market to pull") for generalizing beyond one hand-picked market at a time
- Take-profit / stop overlay with a velocity exception (informational vs. noise moves)
- Slippage in the execution simulator
- Whether `SignalEvent.strength` should scale Portfolio's order quantity
- SQLite-backed data handler (in place of / alongside CSV)
- LLM-assisted idea generation for strategies/exit rules

Regenerate this diagram (or ask Claude to) whenever the pipeline changes — it's plain text, so it's easy to keep in sync rather than letting it drift.
