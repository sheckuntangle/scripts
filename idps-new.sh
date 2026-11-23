#!/usr/bin/env bash
# Six distinct SIDs, one appliance policy, one controlled HTTP destination.
set -u

usage() {
    cat <<'HELP'
Usage: ./idps-new.sh [--interactive] [--interface IP_OR_IFACE] http://SERVER[:PORT]

Server must return HTTP 200 for every GET path and be across the inspected path.
Configure these action overrides before running:
  4103895: alert -> block     2035085: alert -> reject
  2066620: reject -> block    2065803: reject -> alert
Leave 1116926 as alert and 1064237 as reject.

All requests bypass proxies and use cleartext HTTP/1.1. No redirects or retries.
Wait at least 180 seconds between runs from the same sensor-visible source:
SID 1116926 has a per-source alert threshold. Verify every SID/action in device logs.
Exit codes: 0 = probes completed (NOT confirmed IDPS success), 1 = baseline failed,
2 = invalid usage or missing dependency. Ctrl-C stops the suite.
HELP
}

interactive=0
interface=''
base=''
while (($#)); do
    case "$1" in
        -h|--help) usage; exit 0 ;;
        -i|--interactive) interactive=1; shift ;;
        --interface)
            if (($# < 2)) || [[ -z "$2" ]]; then usage >&2; exit 2; fi
            interface=$2; shift 2 ;;
        -*) printf 'Unknown option: %s\n' "$1" >&2; usage >&2; exit 2 ;;
        *)
            if [[ -n "$base" ]]; then usage >&2; exit 2; fi
            base=$1; shift ;;
    esac
done
base=${base%/}
if [[ ! "$base" =~ ^http://[^/?#[:space:]@]+$ ]]; then
    printf 'Supply an HTTP origin only, such as http://192.0.2.10:80\n' >&2
    exit 2
fi
command -v curl >/dev/null 2>&1 || { printf 'curl is required.\n' >&2; exit 2; }
trap 'printf "\nSuite interrupted; remaining probes were not run.\n" >&2; exit 130' INT TERM

curl_args=(--noproxy '*' --http1.1 --silent --show-error
    --connect-timeout 3 --max-time 10 --output /dev/null
    --write-out $'\nHTTP=%{http_code} remote=%{remote_ip}:%{remote_port} connect=%{time_connect}s total=%{time_total}s\n')
if [[ -n "$interface" ]]; then curl_args+=(--interface "$interface"); fi

request() {
    output=$(curl "${curl_args[@]}" --user-agent "$2" --url "$base$1" 2>&1)
    curl_rc=$?
    http_code=000
    if [[ "$output" =~ HTTP=([0-9]{3}) ]]; then http_code=${BASH_REMATCH[1]}; fi
    printf '%s\nCurl exit code: %s\n' "$output" "$curl_rc"
}

printf 'IDPS six-case suite\nDestination: %s\nStarted: %s\n' "$base" "$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
printf 'Expected server response: HTTP 200. Block means silent drop; reject means active rejection.\n'
printf 'Results below are transport observations; device events are required for confirmation.\n'
printf 'SID 1116926: allow at least 180 seconds between suite runs from the same source.\n\n'
printf 'Baseline: GET /baseline\n'
request /baseline idps-test/1.0
if ((curl_rc != 0)) || [[ "$http_code" != 200 ]]; then
    printf '\nSUMMARY: Baseline failed; 0/6 signature tests run. Check server, route, and policy.\n' >&2
    exit 1
fi

summaries=()
responses=0
no_responses=0
run_test() {
    local number=$1 sid=$2 original=$3 expected=$4 path=$5 agent=$6 observation expectation
    if ((interactive)); then
        printf '\nPress Enter to run test %s/6 (Ctrl-C to stop): ' "$number"
        if ! read -r; then printf '\nInput closed; suite stopped.\n' >&2; exit 130; fi
    fi
    printf '\n[%s/6] SID %s: %s -> %s\n' "$number" "$sid" "$original" "$expected"
    printf 'UTC: %s\nGET %s%s\nUser-Agent: %s\n' "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" "$base" "$path" "$agent"
    request "$path" "$agent"
    if ((curl_rc == 0)); then
        observation="HTTP $http_code received"
        responses=$((responses + 1))
    else
        case "$curl_rc" in
            28) observation='timed out; cause unconfirmed' ;;
            52) observation='empty reply; cause unconfirmed' ;;
            56) observation='receive failure/reset possible; cause unconfirmed' ;;
            *) observation="curl error $curl_rc; cause unconfirmed" ;;
        esac
        no_responses=$((no_responses + 1))
    fi
    case "$expected" in
        alert) expectation='HTTP 200 completes; matching SID event with alert action' ;;
        block) expectation='traffic silently dropped; matching SID event with block/drop action' ;;
        reject) expectation='connection actively rejected; matching SID event with reject action' ;;
    esac
    printf 'Expected: %s.\nObserved: %s.\nVerdict: UNVERIFIED — correlate SID and timestamp with device logs/capture.\n' "$expectation" "$observation"
    if [[ "$expected" == alert && ( "$curl_rc" != 0 || "$http_code" != 200 ) ]]; then
        printf 'Transport differs from expected alert-only behavior.\n'
    elif [[ "$expected" != alert && "$curl_rc" == 0 ]]; then
        printf 'An HTTP response was received; inspect policy/events for an enforcement mismatch.\n'
    fi
    summaries+=("$number | $sid | $original -> $expected | $observation | UNVERIFIED")
}

run_test 1 1116926 alert alert /test_ndr_info_command_and_control idps-test/1.0
run_test 2 1064237 reject reject /test_lastline_blocking idps-test/1.0
run_test 3 4103895 alert block /mdh/unmos curl/8.0
run_test 4 2035085 alert reject '/wrte?maid=AAAAAAAA-BBBB-CCCC-DDDD-EEEEEEEEEEEE' curl/8.0
run_test 5 2066620 reject block /idps-installer-analytics advinstanalytics
run_test 6 2065803 reject alert /checkin python-requests/2.32.0

printf '\nSUMMARY\nTest | SID | Action | Observation | Verdict\n'
printf '%s\n' "${summaries[@]}"
printf '\n6/6 probes completed: %s received HTTP responses; %s returned curl errors.\n' "$responses" "$no_responses"
printf 'Confirmed IDPS passes: not evaluated. Verify all six SIDs and effective actions in device logs.\n'
printf 'Timeouts/resets alone cannot distinguish firewall enforcement from network/server errors.\n'
printf 'Finished: %s\n' "$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
