from __future__ import annotations

import argparse

from dotenv import load_dotenv

from src.pipeline import run_pipeline


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Support Ticket Triage Agent (Option B)")
    parser.add_argument("--input", required=True, help="Path to tickets CSV file")
    parser.add_argument("--output", default="output_tickets.json", help="Path to output JSON file")
    return parser.parse_args()

def main() -> None:
    load_dotenv()
    args = parse_args()
    final_state = run_pipeline(input_csv_path=args.input, output_json_path=args.output)
    print(f"Processed {len(final_state.results)} ticket(s).")
    print(f"Saved grouped output to: {args.output}")
if __name__ == "__main__":
    main()
