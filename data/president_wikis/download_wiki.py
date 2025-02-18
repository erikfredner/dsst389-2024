#!/usr/bin/env python3
import argparse
import warnings
import wikipedia
from urllib.parse import urlparse, unquote
from bs4 import GuessedAtParserWarning

# Suppress the BeautifulSoup "GuessedAtParserWarning"
warnings.filterwarnings("ignore", category=GuessedAtParserWarning)

def main():
    parser = argparse.ArgumentParser(
        description="Download a Wikipedia page's plain text content and save it to a file."
    )
    parser.add_argument(
        "page_identifier",
        help=("The title of the Wikipedia page, a full URL to the Wikipedia page, "
              "or (with --id) a page id.")
    )
    parser.add_argument(
        "--id",
        type=int,
        help="The Wikipedia page id to download (overrides page_identifier if provided)."
    )
    args = parser.parse_args()

    try:
        # If page id is provided, use it.
        if args.id is not None:
            page = wikipedia.page(pageid=args.id)
        else:
            # Determine if the input is a URL.
            if args.page_identifier.startswith("http://") or args.page_identifier.startswith("https://"):
                parsed_url = urlparse(args.page_identifier)
                if not parsed_url.path.startswith("/wiki/"):
                    parser.error("URL does not appear to be a valid Wikipedia article URL.")
                # Extract the title from the URL path.
                extracted_title = parsed_url.path.split("/wiki/")[-1]
                extracted_title = unquote(extracted_title)       # Decode URL-encoded characters.
                extracted_title = extracted_title.replace("_", " ")  # Replace underscores with spaces.
                title = extracted_title
            else:
                title = args.page_identifier

            # Try to get the page using the extracted title.
            try:
                page = wikipedia.page(title, auto_suggest=False)
            except wikipedia.DisambiguationError as e:
                # Try to find an exact match (ignoring case) in the disambiguation options.
                exact_matches = [option for option in e.options if option.lower() == title.lower()]
                if exact_matches:
                    page = wikipedia.page(exact_matches[0], auto_suggest=False)
                else:
                    print(f"Ambiguous title '{title}'. Using the first option: {e.options[0]}")
                    page = wikipedia.page(e.options[0], auto_suggest=False)

        content = page.content

        # Create a filename from the page title (lowercase, spaces replaced by hyphens)
        file_name = page.title.lower().replace(" ", "-") + ".txt"

        with open(file_name, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"Page content saved to '{file_name}'")

    except wikipedia.exceptions.PageError:
        print(f"Error: The page '{args.page_identifier}' does not exist.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
