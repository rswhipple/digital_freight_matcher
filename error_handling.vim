:%s/\(.*supabase.*\\\n.*\|.*supabase.*\)/
\   try:\r
\       \1\r
\   except:\r
\       printf("TK")\r
\       exit(1)\r
\/gc
