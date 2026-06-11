import streamlit as st
import subprocess
import socket
import platform
import shutil
import time
import random
from concurrent.futures import ThreadPoolExecutor

st.set_page_config(page_title="NOC Command Suite", layout="centered")

# --- CORE ENGINE ---
def run_command(cmd_list):
    try:
        res = subprocess.run(cmd_list, capture_output=True, text=True, timeout=10)
        return res.stdout if res.stdout else res.stderr
    except Exception as e: 
        return f"Error: {e}"

st.title("Network Operations Center (NOC) Command Suite")

# --- GLOBAL TARGET INPUT ---
st.subheader("Global Diagnostic Target")
target_ip = st.text_input("Enter Target IP for all diagnostics:", "8.8.8.8")
st.divider()


# 1. MONITOR
st.header("1. 📊 System Operations Monitor")
if 'auto_refresh' not in st.session_state: 
    st.session_state.auto_refresh = False

if st.button("Toggle Auto-Refresh"): 
    st.session_state.auto_refresh = not st.session_state.auto_refresh

placeholder = st.empty()
if st.session_state.auto_refresh:
    with placeholder.container():
        c1, c2, c3 = st.columns(3)
        c1.metric("Load", f"{random.randint(60, 90)}%")
        c2.metric("Connections", str(random.randint(100, 200)))
        c3.metric("Status", "Optimal")
    time.sleep(3)
    st.rerun()


# 2. PORT SCANNER (OPTIMIZED)
st.header("2. 🛡️ Port Security Scanner")
scan_target = st.text_input("Target IP for Scan", target_ip)

def check_port(port):
    """Checks if a single port is open."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.5)  # Fast timeout for local network
            if s.connect_ex((scan_target, port)) == 0:
                return port
    except:
        pass
    return None

if st.button("Scan Common Ports"):
    ports = [21, 22, 23, 25, 53, 80, 110, 135, 139, 443, 445, 3306, 3389, 8080]
    with st.spinner("Scanning ports in parallel..."):
        with ThreadPoolExecutor(max_workers=10) as executor:
            open_ports = [p for p in executor.map(check_port, ports) if p is not None]
    
    if open_ports:
        st.success(f"Open Ports Found on {scan_target}: {open_ports}")
    else:
        st.warning("No common ports are open.")


# 3. SUBNET DISCOVERY
st.header("3. 🗺️ Subnet Discovery")
if st.button("Scan Subnet Range"):
    base = ".".join(target_ip.split('.')[:-1])
    with st.spinner("Mapping subnet..."):
        def ping(i):
            ip = f"{base}.{i}"
            # Linux specific ping: -c for count, -W for timeout in seconds
            cmd = ['ping', '-c', '1', '-W', '1', ip]
            return ip if subprocess.run(cmd, capture_output=True).returncode == 0 else None
            
        with ThreadPoolExecutor(max_workers=40) as e:
            discovered = [ip for ip in e.map(ping, range(1, 255)) if ip]
            st.write(discovered)


# 4. DIAGNOSTIC TOOLBOX
st.header("4. ⚡ Diagnostic Toolbox")
tool = st.selectbox("Select Tool", ["ping", "nslookup", "traceroute"])
if st.button(f"Run {tool}"):
    if tool == "ping":
        st.code(run_command(["ping", "-c", "4", target_ip]))
    else:
        st.code(run_command([tool, target_ip]))


# 5. HOST INTERFACES
st.header("5. 💻 Host Interface Adaptor")
if st.button("Show System Config"): 
    st.code(run_command(["ip", "-br", "addr"]))


# 6. TRAFFIC AUDITOR
st.header("6. 🌐 Traffic & Connection Auditor")
if st.button("Audit Active Connections"): 
    st.code(run_command(["ss", "-tunlp"]))


# 7. DNS & LATENCY
st.header("7. 🌐 DNS & Latency")
if st.button("Check Latency"): 
    st.code(run_command(["ping", "-c", "4", target_ip]))


# 8. INTERFACE PERFORMANCE
st.header("8. 📈 Interface Performance")
if st.button("Audit Interface"): 
    st.code(run_command(["ip", "-s", "link"]))


# 9. FIREWALL STATUS
st.header("9. 🛡️ Firewall Security Status")
if st.button("Check Firewall"): 
    st.code(run_command(["sudo", "ufw", "status", "verbose"]))
