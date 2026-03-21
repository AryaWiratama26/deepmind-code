import os
import fnmatch
from pathlib import Path
from typing import List, Dict, Optional

class ContextManager:
    """
    Manages project context by scanning files and providing content to the LLM.
    """
    def __init__(self, root_dir: str = "."):
        """
        Initialize the ContextManager.
        
        Args:
            root_dir (str): The root directory of the project to manage.
        """
        self.root_dir = Path(root_dir).absolute()
        self.ignored_patterns = {".git", "__pycache__", "node_modules", ".venv", "venv", ".dmc"}
        self._load_dmcignore()

    def _load_dmcignore(self):
        """Load additional ignore patterns from .dmcignore file."""
        ignore_file = self.root_dir / ".dmcignore"
        if ignore_file.exists():
            try:
                with open(ignore_file, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            if line.endswith("/"):
                                line = line[:-1]
                            self.ignored_patterns.add(line)
            except Exception:
                pass

    def _is_ignored(self, path: str) -> bool:
        """Check if a path matches any ignore patterns."""
        name = os.path.basename(path)
        # Check direct matches or pattern matches
        for pattern in self.ignored_patterns:
            if fnmatch.fnmatch(name, pattern) or fnmatch.fnmatch(path, pattern):
                return True
            # Also check if any part of the path matches a directory pattern
            parts = Path(path).parts
            if any(fnmatch.fnmatch(p, pattern) for p in parts):
                return True
        return False

    def get_file_tree(self) -> str:
        """
        Generate a string representation of the project's file structure.
        
        Returns:
            str: A formatted string showing the directory and file tree.
        """
        tree = []
        try:
            for root, dirs, files in os.walk(self.root_dir):
                # Filter out ignored directories
                dirs[:] = [d for d in dirs if not self._is_ignored(os.path.join(root, d)) and not d.startswith(".")]
                
                # Skip the root directory name itself in the tree
                if root == str(self.root_dir):
                    rel_root = "."
                else:
                    rel_root = os.path.basename(root)
                
                level = root.replace(str(self.root_dir), "").count(os.sep)
                indent = " " * 4 * level
                tree.append(f"{indent}{rel_root}/")
                sub_indent = " " * 4 * (level + 1)
                for f in files:
                    rel_f_path = os.path.relpath(os.path.join(root, f), self.root_dir)
                    if self._is_ignored(rel_f_path) or f.startswith("."):
                        continue
                    tree.append(f"{sub_indent}{f}")
        except Exception as e:
            return f"Error scanning directory: {str(e)}"
        
        return "\n".join(tree)

    def read_file(self, file_path: str) -> Optional[str]:
        """
        Read the contents of a specific file.
        
        Args:
            file_path (str): Relative path to the file from the project root.
            
        Returns:
            Optional[str]: The file content as a string, or None if the file cannot be read.
        """
        full_path = self.root_dir / file_path
        if not full_path.exists() or not full_path.is_file():
            return None
        
        try:
            with open(full_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception:
            return None

    def get_project_context(self) -> str:
        """
        Construct a context summary for the LLM including the project structure.
        
        Returns:
            str: A string containing the project file tree and instructions for the AI.
        """
        tree = self.get_file_tree()
        return f"Project Structure:\n{tree}\n\n"

    def find_file(self, filename: str) -> Optional[str]:
        """
        Recursively search for a file within the project if the initial path is not found.
        
        Args:
            filename (str): The name of the file to search for.
            
        Returns:
            Optional[str]: The relative path to the file if found, otherwise None.
        """
        if (self.root_dir / filename).exists():
            return filename
            
        for root, dirs, files in os.walk(self.root_dir):
            dirs[:] = [d for d in dirs if not self._is_ignored(os.path.join(root, d))]
            if filename in files:
                rel_path = os.path.relpath(os.path.join(root, filename), self.root_dir)
                return rel_path
        return None
