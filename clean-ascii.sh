for file in /Users/jhester/Desktop/thesis-code/temp/*.txt; do
if [ -f "$file" ]; then
    tr -dc '\0-\177' <$file >/Users/jhester/Desktop/thesis-code/drugscom-older-out-clean/${file##*/}
fi
done

