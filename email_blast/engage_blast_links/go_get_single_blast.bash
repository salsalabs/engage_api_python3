#!/usr/bin/bash
token='P5vbYgrXK5s-_ZPbvX4pJN1AgVWZrbuLTTb2DiU8NbNWAfl3eqrSxaYnIwRqMYmJXOvHfbucJTZ02gA23SERRAb9Z6gZTK24IdKkFdyaLcEHFJ3S_-l-buIgwwxsG6YeUig_EaF1aB6_ENjZFy2vNA'
emailID='e0b50d64-c740-4293-a30c-0035ab1184e6'

python3 get_single_blast.py --token "$token" --emailID "$emailID" $*

