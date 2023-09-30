# In the future, should look like
#   #!/usr/bin/psh
import sys

print(sys.argv[0])

if sys.argv[0] == "bash":
    echo("Execute me directly")@()
    return 1

else:
    echo("Ok")@()
    cd(Path(sys.argv[0]).parent.parent)@()
    files = (find('.') | sort | head('-n', 10))@()
    for f in files.splitlines():
        print(f'Got file {f}')

    tf = tempfile@().stdout
    print(f'Files written to {tf}')
    echo(files)@(o=tf)
    f = input('Check for existence of: (input)')
    if grep(f'{f}$', oe=0) <<< f:
        print('Present')

    else:
        print('Absent')


