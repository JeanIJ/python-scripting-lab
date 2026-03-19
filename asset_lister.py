#!/usr/bin/env python3
import csv, json, argparse
from pathlib import Path

# Fixed type hint from list[str] to list[dict]
def load_assets(path: Path) -> list[dict]: 
    rows = []
    with path.open(newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            r = {k: (v.strip() if isinstance(v, str) else v) for k, v in r.items()}
            # normalize tags to a list of lowercase tokens
            r["tags"] = [t.strip().lower() for t in (r.get("tags","")).split(",") if t.strip()]
            r["criticality"] = r.get("criticality","").strip().lower()
            rows.append(r)
    return rows


# Added type hints, fixed typos, fixed logic, and added the high_only parameter
def filter_assets(rows: list[dict], owner: str = None, tag: str = None, critical_only: bool = False, high_only: bool = False) -> list[dict]: 
    def match(r):
        if critical_only and r.get("criticality") != "critical":
            return False
            
        if owner and r.get("owner","").lower() != owner.lower(): # Fixed typo 'own' to 'owner'
            return False
            
        if tag and tag.lower() not in r.get("tags", []): # Fixed logic tag.upper() to tag.lower()
            return False
            
        # Added condition for high_only
        if high_only and r.get("criticality") != "high":
            return False
        
        return True
    
    return [r for r in rows if match(r)]


def main():
    ap = argparse.ArgumentParser(description="Filter assets from CSV and export to JSON.")
    ap.add_argument("--owner", help="Filter by owner (exact match)")
    ap.add_argument("--tag", help="Filter by tag (lowercase after normalization)")
    ap.add_argument("--critical-only", action="store_true", help="Only include critical assets")

    # Added argument for --high-only
    ap.add_argument("--high-only", action="store_true", help="Only include high priority assets")
    
    ap.add_argument("--infile", default="asset_inventory_list.csv", help="Input CSV") 
    ap.add_argument("--outfile", default="critical_assets.json", help="Output JSON")
    args = ap.parse_args()

    rows = load_assets(Path(args.infile))
    
    # Passed high_only to filter_assets
    out = filter_assets(rows, owner=args.owner, tag=args.tag, critical_only=args.critical_only, high_only=args.high_only) 
    
    Path(args.outfile).write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"Wrote {len(out)} assets to {args.outfile}")


if __name__ == "__main__":
    main()