from scapy.all import sniff, AsyncSniffer, PcapWriter

# Dictionary to store PcapWriter objects for each interface
pcap_writers = {}

# Function to handle each captured packet
def packet_callback(packet, iface):
    pcap_writers[iface].write(packet)

# Specify the interfaces to capture on
interfaces = ['eth0', 'lo']

# Initialize PcapWriter for each interface
for iface in interfaces:
    pcap_writers[iface] = PcapWriter(f"/root/{iface}_capture.pcap", append=True, sync=True)

# Define the BPF filter for ports 443 and 8000
#bpf_filter = "tcp port 443 or tcp port 8000"

# Create a list to hold sniffer threads for each interface
sniffers = []

# Start sniffing on specified interfaces with the BPF filter
for iface in interfaces:
    #sniffer = AsyncSniffer(iface=iface, filter=bpf_filter, prn=lambda pkt, iface=iface: packet_callback(pkt, iface), store=False)
    sniffer = AsyncSniffer(iface=iface, prn=lambda pkt, iface=iface: packet_callback(pkt, iface), store=False)
    sniffer.start()
    sniffers.append(sniffer)

#print(f"Sniffing on interfaces: {interfaces} with filter: {bpf_filter}")
print(f"Sniffing on interfaces: {interfaces}")

# Run indefinitely, capturing packets
try:
    while True:
        pass
except KeyboardInterrupt:
    print("Stopping sniffers...")
    for sniffer in sniffers:
        sniffer.stop()

    print("All sniffers stopped.")
