import argparse
import sys
from pathlib import Path
from .pubmed_fetcher import PubMedFetcher


def main():
    parser = argparse.ArgumentParser(
        description="Fetch research papers from PubMed with pharmaceutical/biotech company authors",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "cancer immunotherapy"
  %(prog)s "CRISPR gene editing" --max-results 50 --output results.csv
  %(prog)s "COVID-19 vaccine" --debug --email user@example.com
        """
    )
    
    parser.add_argument(
        'query',
        help='Search query for PubMed (supports full PubMed query syntax)'
    )
    
    parser.add_argument(
        '-f', '--file',
        default='research_papers.csv',
        help='Output CSV filename (default: research_papers.csv)'
    )
    
    parser.add_argument(
        '-d', '--debug',
        action='store_true',
        help='Print debug information during execution'
    )
    
    # parser.add_argument(
    #     '-h', '--help',
    #     action='help',
    #     help='Display usage instructions'
    # )
    
    parser.add_argument(
        '--max-results',
        type=int,
        default=100,
        help='Maximum number of papers to fetch (default: 100)'
    )
    
    parser.add_argument(
        '--email',
        default='user@example.com',
        help='Email address for NCBI API identification (default: user@example.com)'
    )
    
    parser.add_argument(
        '--api-key',
        help='NCBI API key for increased rate limits (optional)'
    )
    
    args = parser.parse_args()
    if args.max_results <= 0:
        print("Error: --max-results must be a positive integer", file=sys.stderr)
        sys.exit(1)
    if args.debug:
        print(f"Initializing PubMed fetcher with email: {args.email}")
        if args.api_key:
            print(f"Using API key: {args.api_key[:8]}...")
    
    fetcher = PubMedFetcher(email=args.email, api_key=args.api_key)
    
    try:
        papers = fetcher.fetch_and_filter_papers(
            query=args.query,
            max_results=args.max_results,
            output_file=args.file
        )
        
        if papers:
            print(f"\nSuccessfully processed {len(papers)} papers with company affiliations.")
            print(f"Results saved to: {args.file}")
            
            if args.debug:
                print("\nSample results:")
                for i, paper in enumerate(papers[:3]):
                    print(f"\n{i+1}. {paper.title}")
                    print(f"   PubMed ID: {paper.pubmed_id}")
                    print(f"   Company Authors: {', '.join(paper.non_academic_authors[:2])}")
                    if len(paper.non_academic_authors) > 2:
                        print(f"   ... and {len(paper.non_academic_authors) - 2} more")
        else:
            print("\nNo papers found with pharmaceutical/biotech company authors.")
            if not Path(args.file).exists():
                fetcher.save_to_csv([], args.file)
                print(f"Empty results file created: {args.file}")
    
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()