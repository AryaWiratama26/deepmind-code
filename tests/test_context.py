import os
from pathlib import Path
from deepmind_code.core.context import ContextManager

def test_context_manager_initialization(tmp_path):
    ctx = ContextManager(root_dir=tmp_path)
    assert str(ctx.root_dir) == str(tmp_path.resolve())
    assert ".git" in ctx.ignored_patterns
    assert "node_modules" in ctx.ignored_patterns

def test_load_dmcignore(tmp_path):
    ignore_file = tmp_path / ".dmcignore"
    ignore_file.write_text("*.log\nsecrets/\n# comment\n")
    
    ctx = ContextManager(root_dir=tmp_path)
    assert "*.log" in ctx.ignored_patterns
    assert "secrets" in ctx.ignored_patterns
    
    assert ctx._is_ignored("test.log") == True
    assert ctx._is_ignored("secrets/key.txt") == True
    assert ctx._is_ignored("normal.py") == False

def test_get_file_tree_ignores(tmp_path):
    (tmp_path / "secrets").mkdir()
    (tmp_path / "secrets" / "key.txt").write_text("shh")
    (tmp_path / "test.log").write_text("error")
    (tmp_path / "app.py").write_text("print('hello')")
    
    ignore_file = tmp_path / ".dmcignore"
    ignore_file.write_text("*.log\nsecrets\n")
    
    ctx = ContextManager(root_dir=tmp_path)
    tree = ctx.get_file_tree()
    
    assert "app.py" in tree
    assert "test.log" not in tree
    assert "secrets" not in tree
    assert "key.txt" not in tree

def test_find_file(tmp_path):
    # Create a test directory structure
    test_dir = tmp_path / "subdir"
    test_dir.mkdir()
    test_file = test_dir / "test_file.txt"
    test_file.write_text("hello deepmind")
    
    ctx = ContextManager(root_dir=tmp_path)
    found_path = ctx.find_file("test_file.txt")
    
    assert found_path is not None
    assert str(found_path).endswith("test_file.txt")
    assert "subdir" in str(found_path)

def test_read_file(tmp_path):
    test_file = tmp_path / "dummy.py"
    test_file.write_text("print('test')")
    
    ctx = ContextManager(root_dir=tmp_path)
    content = ctx.read_file("dummy.py")
    assert content == "print('test')"
    
def test_read_nonexistent_file(tmp_path):
    ctx = ContextManager(root_dir=tmp_path)
    content = ctx.read_file("does_not_exist.txt")
    assert content is None
