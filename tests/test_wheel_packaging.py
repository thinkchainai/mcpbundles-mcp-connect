"""Regression tests for wheel packaging."""

from __future__ import annotations

import subprocess
import sys
import zipfile
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[1]


def test_built_wheel_includes_fastmcp_subpackage() -> None:
    dist_dir = PACKAGE_ROOT / "dist"
    dist_dir.mkdir(exist_ok=True)

    build = subprocess.run(
        ["uv", "build", "--out-dir", str(dist_dir)],
        cwd=PACKAGE_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert build.returncode == 0

    wheels = sorted(dist_dir.glob("*.whl"), key=lambda path: path.stat().st_mtime)
    assert wheels, "uv build did not produce a wheel"

    wheel = wheels[-1]
    with zipfile.ZipFile(wheel) as archive:
        names = archive.namelist()

    fastmcp_paths = [
        name
        for name in names
        if name.startswith("mcpbundles_mcp_connect/fastmcp/")
        and name.endswith(".py")
    ]
    assert fastmcp_paths, f"wheel missing fastmcp subpackage; entries: {names}"
    assert any(name.endswith("fastmcp/provider.py") for name in names)
    assert any(name.endswith("mcpbundles_mcp_connect/py.typed") for name in names)


def test_installed_wheel_imports_public_api(tmp_path: Path) -> None:
    dist_dir = PACKAGE_ROOT / "dist"
    wheels = sorted(dist_dir.glob("*.whl"), key=lambda path: path.stat().st_mtime)
    assert wheels, "run test_built_wheel_includes_fastmcp_subpackage first"

    wheel = wheels[-1]
    venv_dir = tmp_path / "venv"
    subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], check=True)
    pip = venv_dir / "bin" / "pip"
    python = venv_dir / "bin" / "python"

    subprocess.run([str(pip), "install", str(wheel)], check=True, capture_output=True)
    import_check = subprocess.run(
        [
            str(python),
            "-c",
            (
                "from mcpbundles_mcp_connect import "
                "McpbundlesConnectProvider, mcpbundles_fastmcp; "
                "print(McpbundlesConnectProvider.__name__, mcpbundles_fastmcp.__name__)"
            ),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "McpbundlesConnectProvider mcpbundles_fastmcp" in import_check.stdout
