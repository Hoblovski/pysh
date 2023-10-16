from .exec import Run, Cap
from .command import Command, CommitResult, CommitResKind
from .errors import PyShError, PyShCommitError
from .contexts import ChDir

from .prelude import (
    chmod,
    fd,
    tr,
    find,
    git,
    git,
    grep,
    head,
    make,
    rg,
    sed,
    sort,
    tail,
    vim,
    touch,
    ls_,
    echo_,
    cat_,
    cp_,
    mkdir_,
    rm_,
    mv_,
    tee_,
)

# version check
import sys
if sys.version_info < (3, 11):
    print(f'Pysh runs on python >= 3.11. Got:\n{sys.version}', file=sys.stderr)
    exit(1)
