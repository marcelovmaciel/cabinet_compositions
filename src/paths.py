"""Resolved producer paths and the single writable build area."""
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
INPUTS = PROJECT / 'data/normalized'
SOURCE = PROJECT / 'data/source'
PROJECTION = PROJECT / 'data/projection'
BUILD = PROJECT / 'build'
PUBLISHED = PROJECT / 'releases/2026-03-19-v6-election-v1'


def safe_path(path):
    path = Path(path).absolute()
    if any(p.is_symlink() for p in (path, *path.parents)):
        raise ValueError(f'Symlink paths are not supported: {path}')
    resolved = path.resolve()
    if not resolved.is_relative_to(PROJECT):
        raise ValueError(f'Path must be inside independent producer {PROJECT}: {path}')
    return resolved


def build_path(path):
    path = safe_path(path)
    if path == BUILD or not path.is_relative_to(BUILD):
        raise ValueError(f'Generated output must be inside {BUILD}: {path}')
    return path
