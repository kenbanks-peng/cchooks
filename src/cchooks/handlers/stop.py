import logging
import subprocess
import os
from typing import Dict, Any, Set


def get_changed_files(cwd: str) -> Set[str]:
    """Get list of changed files from git status."""
    try:
        # Get staged and unstaged changes
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD"],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode != 0:
            logging.warning(f"Git diff failed: {result.stderr}")
            return set()

        files = (
            set(result.stdout.strip().split("\n")) if result.stdout.strip() else set()
        )

        # Also get staged files
        staged_result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
        )

        if staged_result.returncode == 0 and staged_result.stdout.strip():
            files.update(staged_result.stdout.strip().split("\n"))

        return files
    except Exception as e:
        logging.error(f"Error getting changed files: {e}")
        return set()


def get_file_extensions(files: Set[str]) -> Set[str]:
    """Extract unique file extensions from file paths."""
    extensions = set()
    for file in files:
        if "." in file:
            ext = file.split(".")[-1].lower()
            extensions.add(ext)
    return extensions


def get_git_root(cwd: str) -> str:
    """Get the git root directory."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            return result.stdout.strip()
        return cwd
    except Exception:
        return cwd


def filter_existing_files(files: Set[str], cwd: str, git_root: str) -> Set[str]:
    """Filter files to only include those that exist, handling git root vs cwd differences."""
    existing_files = set()
    for f in files:
        # Try relative to current working directory first
        cwd_path = os.path.join(cwd, f)
        if os.path.exists(cwd_path):
            existing_files.add(f)
            continue

        # Try removing the common prefix if cwd is a subdirectory of git root
        try:
            rel_cwd = os.path.relpath(cwd, git_root)
            if f.startswith(rel_cwd + "/"):
                relative_file = f[len(rel_cwd) + 1 :]
                if os.path.exists(os.path.join(cwd, relative_file)):
                    existing_files.add(relative_file)  # Add the corrected relative path
                    continue
        except ValueError:
            # Paths are on different drives or similar
            pass

        # Try the file path as-is from git root (fallback)
        git_path = os.path.join(git_root, f)
        if os.path.exists(git_path):
            existing_files.add(f)

    return existing_files


def run_linting_formatting(cwd: str, extensions: Set[str], files: Set[str]) -> None:
    """Run appropriate linting/formatting tools based on file extensions."""

    # Get git root to handle file paths correctly
    git_root = get_git_root(cwd)

    # Python files
    if any(ext in extensions for ext in ["py"]):
        python_files = list(
            filter_existing_files(
                {f for f in files if f.endswith(".py")}, cwd, git_root
            )
        )
        if python_files:
            logging.info(
                f"Running Python linting/formatting on {len(python_files)} files: {python_files}"
            )

            # Run ruff format
            try:
                subprocess.run(["ruff", "format"] + python_files, cwd=cwd, check=False)
                logging.info("Ruff formatting completed")
            except FileNotFoundError:
                logging.warning("Ruff not found, skipping formatting")

            # Run ruff check
            try:
                subprocess.run(
                    ["ruff", "check", "--fix"] + python_files, cwd=cwd, check=False
                )
                logging.info("Ruff linting completed")
            except FileNotFoundError:
                logging.warning("Ruff not found, skipping linting")

    # JavaScript/TypeScript files
    if any(ext in extensions for ext in ["js", "jsx", "ts", "tsx"]):
        js_files = list(
            filter_existing_files(
                {
                    f
                    for f in files
                    if any(f.endswith(f".{ext}") for ext in ["js", "jsx", "ts", "tsx"])
                },
                cwd,
                git_root,
            )
        )
        if js_files:
            logging.info(
                f"Running JS/TS linting/formatting on {len(js_files)} files: {js_files}"
            )

            # Try prettier first
            try:
                subprocess.run(["prettier", "--write"] + js_files, cwd=cwd, check=False)
                logging.info("Prettier formatting completed")
            except FileNotFoundError:
                logging.warning("Prettier not found, skipping formatting")

            # Try eslint
            try:
                subprocess.run(["eslint", "--fix"] + js_files, cwd=cwd, check=False)
                logging.info("ESLint completed")
            except FileNotFoundError:
                logging.warning("ESLint not found, skipping linting")

    # JSON files
    if "json" in extensions:
        json_files = list(
            filter_existing_files(
                {f for f in files if f.endswith(".json")}, cwd, git_root
            )
        )
        if json_files:
            logging.info(
                f"Running JSON formatting on {len(json_files)} files: {json_files}"
            )
            try:
                subprocess.run(
                    ["prettier", "--write"] + json_files, cwd=cwd, check=False
                )
                logging.info("JSON formatting completed")
            except FileNotFoundError:
                logging.warning("Prettier not found for JSON formatting")

    # Go files
    if "go" in extensions:
        go_files = list(
            filter_existing_files(
                {f for f in files if f.endswith(".go")}, cwd, git_root
            )
        )
        if go_files:
            logging.info(f"Running Go formatting on {len(go_files)} files: {go_files}")
            try:
                subprocess.run(["gofmt", "-w"] + go_files, cwd=cwd, check=False)
                logging.info("Go formatting completed")
            except FileNotFoundError:
                logging.warning("gofmt not found, skipping Go formatting")

    # Markdown files
    if any(ext in extensions for ext in ["md", "markdown"]):
        md_files = list(
            filter_existing_files(
                {
                    f
                    for f in files
                    if any(f.endswith(f".{ext}") for ext in ["md", "markdown"])
                },
                cwd,
                git_root,
            )
        )
        if md_files:
            logging.info(
                f"Running Markdown formatting on {len(md_files)} files: {md_files}"
            )
            try:
                subprocess.run(["prettier", "--write"] + md_files, cwd=cwd, check=False)
                logging.info("Markdown formatting completed")
            except FileNotFoundError:
                logging.warning("Prettier not found for Markdown formatting")


def stop(data: Dict[str, Any]) -> None:
    try:
        logging.info(f"Stop handler called with data: {data}")

        # Get the current working directory from the data
        cwd = data.get("cwd", os.getcwd())

        # Get changed files from git
        changed_files = get_changed_files(cwd)

        if changed_files:
            logging.info(
                f"Found {len(changed_files)} changed files: {list(changed_files)}"
            )

            # Get file extensions
            extensions = get_file_extensions(changed_files)
            logging.info(f"File extensions found: {list(extensions)}")

            # Run appropriate linting/formatting
            run_linting_formatting(cwd, extensions, changed_files)
        else:
            logging.info("No changed files found")

        # Play completion sound
        subprocess.run(["afplay", "/System/Library/Sounds/Blow.aiff"], check=False)

    except Exception as e:
        logging.error(f"Error in stop handler: {e}")
