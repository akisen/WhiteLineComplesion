for i in `seq 0 12`
do

  echo "[$i]" ` date '+%y/%m/%d %H:%M:%S'` "connected."
  open <<https://colab.research.google.com/drive/12zdsi_7rCkUKP05KLENFUL7mrLekagBn#scrollTo=EhGBEGk962fh>>
  sleep 3600
done