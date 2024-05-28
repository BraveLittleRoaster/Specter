#!/bin/sh
echo "[-] Updating Tool..."
eval $UPDATE_CMD
echo "[-] List current working directory..."
ls -lah .
#echo "[-] Checking connection to the proxy server..."
#curl -vvv -m 5 http://www.example.com:8000/ || (echo "Proxy server not reachable. Exiting."; exit 1)
echo "====================================================="
echo "\t\tENV VARIABLES\t\t"
echo "====================================================="
echo "[-] CMDLINE_EXEC: $CMDLINE_EXEC"
echo "[-] TARGET_URL: $TARGET_URL"
echo "[-] TARGET_HOST: $TARGET_HOST"
echo "[-] TARGET_PORT: $TARGET_PORT"
echo "[-] INJECTION_POINT: $INJECTION_POINT"
echo "[-] POST_DATA: $POST_DATA"
echo "[-] FILE_UPLOAD: $FILE_UPLOAD"
echo "[-] FILE_INCLUDE: $FILE_INCLUDE"
echo "[-] REMOTE_COMMAND: $REMOTE_COMMAND"
echio "[-] TARGET_SCAN: $TARGET_SCAN"
echo "====================================================="

# Construct the command by replacing placeholders with actual environment variable values
CMD=$(echo $CMDLINE_EXEC | sed -e "s|\${TARGET_URL}|$TARGET_URL|g" \
                              -e "s|\${TARGET_HOST}|$TARGET_HOST|g" \
                              -e "s|\${TARGET_PORT}|$TARGET_PORT|g" \
                              -e "s|\${INJECTION_POINT}|$INJECTION_POINT|g" \
                              -e "s|\${REMOTE_COMMAND}|$REMOTE_COMMAND|g" \
                              -e "s|\${FILE_UPLOAD}|$FILE_UPLOAD|g" \
                              -e "s|\${FILE_INCLUDE}|$FILE_INCLUDE|g" \
                              -e "s|\${POST_DATA}|$POST_DATA|g" \
                              -e "s|\${TARGET_SCAN}|$TARGET_SCAN|g")

echo "[-] Command to execute: $CMD"
echo "[-] Launching $APP_NAME..."
sh -c "$CMD"

# Uncomment to halt the container for debugging.
#tail -f /dev/null
exit