import 'package:flutter/material.dart';
import 'package:flutter_v2ray/flutter_v2ray.dart';

void main() => runApp(const MaterialApp(home: VpnHome()));

class VpnHome extends StatefulWidget {
  const VpnHome({super.key});
  @override
  State<VpnHome> createState() => _VpnHomeState();
}

class _VpnHomeState extends State<VpnHome> {
  late FlutterV2ray v2ray;
  bool connected = false;
  // ТВОЙ КОНФИГ
  String config = "vless://uuid@host:port?security=reality&sni=google.com&fp=chrome&type=grpc&serviceName=grpc#MyVPN";

  @override
  void initState() {
    super.initState();
    v2ray = FlutterV2ray(onStatusChanged: (status) {
      setState(() => connected = status.state == 'CONNECTED');
    });
    v2ray.initializeV2Ray();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: ElevatedButton(
          onPressed: () async {
            if (connected) {
              await v2ray.stopV2Ray();
            } else if (await v2ray.requestPermission()) {
              await v2ray.startV2Ray(remark: "VPN", config: config);
            }
          },
          child: Text(connected ? "STOP" : "START VLESS"),
        ),
      ),
    );
  }
}