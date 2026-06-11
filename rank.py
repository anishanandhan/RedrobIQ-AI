#!/usr/bin/env python3
"""
RedrObIQ Ranker — Intelligent Candidate Ranking for Senior AI Engineer (Founding Team)
by Anish (VIT Chennai / CyStar IIT Madras)

This script acts as the entry point coordinator for parsing arguments, 
reading input profiles, scoring candidates via the app modular engine, 
and writing the sorted, formatted output shortlist.
"""

import json
import csv
import sys
import argparse
from app.services.scoring import score_candidate
from app.services.reasoning import generate_reasoning

def main():
    parser = argparse.ArgumentParser(description="RedrObIQ Candidate Ranker CLI")
    parser.add_argument("--candidates", required=True, help="Path to candidates.jsonl")
    parser.add_argument("--out", required=True, help="Output CSV path")
    parser.add_argument("--top", type=int, default=100, help="Number of candidates to return")
    args = parser.parse_args()

    print(f"Loading candidates from {args.candidates} ...")
    
    scored = []
    count = 0
    errors = 0

    try:
        with open(args.candidates, "r", encoding="utf-8") as f:
            # Peek at the first character to determine format
            first_char = ""
            for char in f.read(100):
                if not char.isspace():
                    first_char = char
                    break
            f.seek(0)
            
            if first_char == "[":
                # Parse as a single JSON array
                try:
                    candidates = json.load(f)
                    if isinstance(candidates, list):
                        for candidate in candidates:
                            try:
                                score, breakdown = score_candidate(candidate)
                                scored.append((score, candidate, breakdown))
                                count += 1
                            except Exception:
                                errors += 1
                    else:
                        try:
                            score, breakdown = score_candidate(candidates)
                            scored.append((score, candidates, breakdown))
                            count += 1
                        except Exception:
                            errors += 1
                except Exception:
                    errors = 1 # file-level parse failure
            else:
                # Parse line-by-line (JSONL)
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        candidate = json.loads(line)
                        score, breakdown = score_candidate(candidate)
                        scored.append((score, candidate, breakdown))
                        count += 1
                        if count % 10000 == 0:
                            print(f"  Processed {count:,} candidates...")
                    except Exception:
                        errors += 1
                        continue
    except FileNotFoundError:
        print(f"Error: Candidate file not found at '{args.candidates}'")
        sys.exit(1)
    except OSError as e:
        print(f"Error reading candidates file: {e}")
        sys.exit(1)

    print(f"Processed {count:,} candidates ({errors} errors). Sorting...")
    
    # Sort by score descending, then candidate_id ascending as tie-breaker
    scored.sort(key=lambda x: (-x[0], x[1]["candidate_id"]))
    
    top = scored[:args.top]
    
    print(f"Writing top {len(top)} candidates to {args.out} ...")
    
    try:
        with open(args.out, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
            writer.writerow(["candidate_id", "rank", "score", "reasoning"])
            for rank, (score, candidate, breakdown) in enumerate(top, 1):
                cid = candidate["candidate_id"]
                reasoning = generate_reasoning(candidate, breakdown)
                writer.writerow([cid, rank, f"{score:.6f}", reasoning])
    except OSError as e:
        print(f"Error writing output file: {e}")
        sys.exit(1)
    
    print("Ranking run complete successfully.")
    if top:
        print(f"Top candidate: {top[0][1]['candidate_id']} (Score: {top[0][0]:.4f})")
        print(f"Score range: {top[0][0]:.4f} -> {top[-1][0]:.4f}")

if __name__ == "__main__":
    main()
