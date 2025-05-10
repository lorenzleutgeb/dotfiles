# https://tratt.net/laurie/blog/2024/faster_shell_startup_with_shell_switching.html
case $- in
*i* )
   …/bin/fish --version > /dev/null && exec …/bin/fish
   echo "Couldn't run '…/bin/fish'" > /dev/stderr
;;
esac
