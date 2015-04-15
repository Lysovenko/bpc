#!/bin/bash
xgettext --language=Python -cNOTE -o TkC.pot ../../*.py
msguniq  TkC.pot -u -o TkC.pot
for i in *.po
do
 msgmerge -U "$i" TkC.pot
 fnam="../locale/${i%.po}/LC_MESSAGES/TkC.mo"
 if [ "$i" -nt "$fnam" ] 
 then
  echo $fnam
  rm -f "$fnam"
  msgfmt "$i" -o "$fnam"
 fi
done


