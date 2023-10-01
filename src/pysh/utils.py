from pathlib import Path


def ensure_path(p: str | Path) -> Path:
    if isinstance(p, Path):
        return p
    if isinstance(p, str):
        return Path(p)


def timeout_to_seconds(x: int | str) -> int:
    if isinstance(x, int):
        return x
    # TODO: Support 3m24s
    num = int(x[:-1])
    match x[-1].lower():
        case "s":
            return num
        case "m":
            return num * 60
        case "h":
            return num * 60 * 60
        case _:
            raise ValueError(f"Unrecognized timeout {x}")
