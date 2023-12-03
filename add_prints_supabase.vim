#:%s/\(.*supabase.*\\\n.*\|.*supabase.*\)/
#\=printf("print(\'Line %d: \')", line('.'))\r
#\        \1\r
#\/gc
:%s/\(.*supabase.*\\\n.*\|.*supabase.*\)/\=printf("\t\tprint(\"Line %d\")\r%s", line('.'), submatch(0))/gc

