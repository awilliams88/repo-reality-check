from __future__ import annotations

# Gradio CSS overrides create a distinct terminal-review interface.
CUSTOM_CSS = """
body, .gradio-container {
    background-color: #090b0a !important;
    color: #ecfccb !important;
    font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
}
#rr-header {
    text-align: center;
    margin: 0 auto 0.65rem auto;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}
#rr-header h1 {
    color: #a3e635 !important;
    font-size: 2.7rem !important;
    font-weight: 760 !important;
    letter-spacing: 0 !important;
}
#rr-header p {
    color: #fca5a5 !important;
    font-size: 1.08rem !important;
}
#rr-kicker {
    width: fit-content;
    max-width: 92%;
    margin: 0 auto 1.5rem auto;
    padding: 0.72rem 1.6rem !important;
    background-color: rgba(163, 230, 53, 0.08) !important;
    border: 1px solid rgba(163, 230, 53, 0.45) !important;
    border-radius: 8px !important;
    text-align: center;
    color: #ecfccb !important;
}
.rr-main-grid, .rr-card-grid, .rr-example-grid, .rr-control-row {
    gap: 1rem !important;
    align-items: stretch !important;
}
.rr-main-grid > .form, .rr-main-grid > .row, .rr-main-grid > div,
.rr-card-grid > .form, .rr-card-grid > .row, .rr-card-grid > div,
.rr-example-grid > .form, .rr-example-grid > .row, .rr-example-grid > div {
    display: flex !important;
    flex-wrap: wrap !important;
    gap: 1rem !important;
}
.rr-input-panel, .rr-output-panel, .rr-analysis-section, .rr-examples-section {
    background-color: #121512 !important;
    border: 1px solid rgba(163, 230, 53, 0.22) !important;
    border-radius: 8px !important;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.32) !important;
    padding: 1.15rem !important;
}
.rr-analysis-section, .rr-examples-section {
    margin-top: 1rem !important;
}
.rr-input-panel, .rr-output-panel {
    flex: 1 1 340px !important;
}
.rr-input-panel h3, .rr-output-panel h3, .rr-analysis-section h3, .rr-examples-section h3 {
    color: #bef264 !important;
    margin: 0 0 0.75rem 0 !important;
}
#rr-notes-input textarea, .rr-output-card textarea, .rr-log-box textarea {
    background-color: #080a08 !important;
    color: #f7fee7 !important;
    border-radius: 8px !important;
    line-height: 1.5 !important;
    overflow-wrap: anywhere !important;
}
#rr-notes-input textarea, .rr-log-box textarea {
    border: 1px solid rgba(163, 230, 53, 0.34) !important;
}
.rr-run-btn {
    background: #a3e635 !important;
    color: #090b0a !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 760 !important;
    min-height: 52px !important;
}
.rr-output-card {
    min-width: 0 !important;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}
.rr-card-grid .block {
    flex: 1 1 280px !important;
    min-width: 0 !important;
}
.rr-pulse-card textarea { border: 1px solid rgba(163, 230, 53, 0.5) !important; }
.rr-risks-card textarea { border: 1px solid rgba(248, 113, 113, 0.48) !important; }
.rr-wins-card textarea { border: 1px solid rgba(45, 212, 191, 0.44) !important; }
.rr-reality-card textarea { border: 1px solid rgba(251, 191, 36, 0.48) !important; }
.rr-plan-card textarea { border: 1px solid rgba(96, 165, 250, 0.44) !important; }
.rr-share-card textarea { border: 1px solid rgba(232, 121, 249, 0.42) !important; }
.rr-example-card {
    flex: 1 1 250px !important;
    background-color: #080a08 !important;
    border: 1px solid rgba(163, 230, 53, 0.22) !important;
    border-radius: 8px !important;
    padding: 0.85rem !important;
}
.rr-example-head {
    display: flex;
    justify-content: space-between;
    gap: 0.8rem;
    color: #ecfccb;
    font-weight: 740;
}
.rr-example-head strong {
    color: #fca5a5;
    white-space: nowrap;
}
.rr-example-copy p {
    color: #d9f99d;
    margin: 0.45rem 0 0 0;
    line-height: 1.45;
}
#rr-links {
    text-align: center;
    margin-top: 1rem;
    color: #bef264 !important;
}
"""
