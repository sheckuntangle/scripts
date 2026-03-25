#!/bin/sh

# Defaults
INTERACTIVE=0
RUN_ALERTS=0
RUN_REJECTS=0
RUN_ALL=1

# Parse arguments for the interactive flag and test categories
for arg in "$@"; do
    case $arg in
        -i|--interactive)
            INTERACTIVE=1
            ;;
        -a|--alerts)
            RUN_ALERTS=1
            RUN_ALL=0
            ;;
        -r|--rejects)
            RUN_REJECTS=1
            RUN_ALL=0
            ;;
        -h|--help)
            echo "Usage: $0 [-i|--interactive] [-a|--alerts] [-r|--rejects]"
            echo "  -i, --interactive : Pause between tests and prompt to continue."
            echo "  -a, --alerts      : Run only the ALERT signature tests."
            echo "  -r, --rejects     : Run only the REJECT signature tests."
            exit 0
            ;;
    esac
done

# If no specific test category was selected, run both
if [ "$RUN_ALL" -eq 1 ]; then
    RUN_ALERTS=1
    RUN_REJECTS=1
fi

# Function to handle the pause between tests
pause_step() {
    if [ "$INTERACTIVE" -eq 1 ]; then
        while true; do
            printf "Proceed ahead? (press 'y' to continue): "
            read choice
            if [ "$choice" = "y" ] || [ "$choice" = "Y" ]; then
                break
            else
                echo "Please press 'y' to proceed."
            fi
        done
        echo ""
    else
        sleep 2
    fi
}

# ==========================================
# ALERT TESTS (Using Reliable URI Triggers)
# ==========================================
if [ "$RUN_ALERTS" -eq 1 ]; then
    echo "========================================"
    echo " RUNNING ALERT TESTS"
    echo "========================================"
    echo ""

    echo "Test A1: SID 2049400 - /etc/passwd Detected in URI"
    echo "Command: curl -s \"http://example.com/etc/passwd\""
    curl -s "http://example.com/etc/passwd" > /dev/null
    echo "-> Request sent (check firewall logs for alert)."
    echo ""
    pause_step

    echo "Test A2: SID 2033891 - Observed Suspicious Request nc.exe in URI"
    echo "Command: curl -s \"http://example.com/nc.exe\""
    curl -s "http://example.com/nc.exe" > /dev/null
    echo "-> Request sent (check firewall logs for alert)."
    echo ""
    pause_step

    echo "Test A3: SID 2029923 - IP Check (ip.jsontest.com)"
    echo "Command: curl -s \"http://ip.jsontest.com/\""
    curl -s "http://ip.jsontest.com/" > /dev/null
    echo "-> Request sent (check firewall logs for alert)."
    echo ""
    pause_step
fi

# ==========================================
# REJECT TESTS (Using Reliable SQLi Triggers)
# ==========================================
if [ "$RUN_REJECTS" -eq 1 ]; then
    echo "========================================"
    echo " RUNNING REJECT TESTS"
    echo "========================================"
    echo "Note: Using 5-second timeout (-m 5) in case firewall drops packets silently."
    echo ""

    echo "Test R1: SID 2007337 - ContentNow SQL Injection Attempt (UNION SELECT)"
    echo "Command: curl -v -m 5 \"http://example.com/index.php?pageid=1%20UNION%20SELECT%20username,password\""
    curl -v -m 5 "http://example.com/index.php?pageid=1%20UNION%20SELECT%20username,password"
    echo ""
    pause_step

    echo "Test R2: SID 2006124 - Mxmania File Upload Manager (detail.asp ID UNION SELECT)"
    echo "Command: curl -v -m 5 \"http://example.com/detail.asp?ID=1%20UNION%20SELECT%20username,password\""
    curl -v -m 5 "http://example.com/detail.asp?ID=1%20UNION%20SELECT%20username,password"
    echo ""
    pause_step

    echo "Test R3: SID 2005082 - ExoPHPDesk SQL Injection Attempt (faq.php id UNION SELECT)"
    echo "Command: curl -v -m 5 \"http://example.com/faq.php?id=1%20UNION%20SELECT%20username,password\""
    curl -v -m 5 "http://example.com/faq.php?id=1%20UNION%20SELECT%20username,password"
    echo ""
    pause_step
fi

echo "Testing complete."
