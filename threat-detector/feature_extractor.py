from datetime import datetime
import logging


SURICATA_TO_MODEL = {
    'flow.duration': 'flow_duration',
    'flow.pkts_toserver': 'fwd_pkts',
    'flow.pkts_toclient': 'bwd_pkts',
    # 'flow.bytes_toserver': 'fwd_bytes',
    # 'flow.bytes_toclient': 'bwd_bytes',
    'dest_port': 'dst_port',
    'tcp.ack': 'ack_flag',
    'tcp.syn': 'syn_flag',
    'tcp.fin': 'fin_flag',
    'tcp.psh': 'psh_flag'
}

def extract_features(flat_entry):
    flow_duration = get_duration(flat_entry.get('flow.start'), flat_entry.get('flow.end'))
    if flow_duration is None:
        logging.warning(f"Flow duration could not be computed. Flat entry: {flat_entry}")
        return None
    flat_entry['flow.duration'] = flow_duration

    features = {}
    for suricata_key, model_key in SURICATA_TO_MODEL.items():
        val = flat_entry.get(suricata_key)
        # if val is None:
        #     logging.warning(f"Missing feature: '{suricata_key}' in input entry: {flat_entry}.")
        features[model_key] = normalize_value(val)
    return features

def parse_iso_timestamp(ts: str) -> datetime:
    return datetime.fromisoformat(
        ts.replace("Z", "+00:00").replace("+0000", "+00:00")
    )

def get_duration(start_str, end_str):
    try:
        start = parse_iso_timestamp(start_str)
        end = parse_iso_timestamp(end_str)
        return int((end - start).total_seconds() * 1_000_000)
    except Exception as e:
        logging.error(f"Error parsing timestamps: start='{start_str}', end='{end_str}'. Error: {e}")
        return None


def normalize_value(v):
    if isinstance(v, bool):
        return int(v)
    if v is None:
        return 0
    return v