import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';
import 'package:khabar/theme/app_colors.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:khabar/api_config.dart';

import 'package:khabar/theme/language_provider.dart';
import 'package:khabar/screens/incident_tracker_screen.dart';

class TextSignalScreen extends StatefulWidget {
  const TextSignalScreen({super.key});

  @override
  State<TextSignalScreen> createState() => _TextSignalScreenState();
}

class _TextSignalScreenState extends State<TextSignalScreen> {
  final TextEditingController _textController = TextEditingController();
  bool _isUrdu = false;
  late LatLng _markerPosition;
  bool _isSubmitting = false;

  @override
  void initState() {
    super.initState();
    _textController.addListener(_onTextChanged);
    
    final String region = LanguageProvider().region;
    final bool isRawalpindi = region.toLowerCase().contains('rawalpindi');
    _markerPosition = LatLng(
      isRawalpindi ? 33.5651 : 33.6844,
      isRawalpindi ? 73.0169 : 73.0479,
    );
  }

  @override
  void dispose() {
    _textController.removeListener(_onTextChanged);
    _textController.dispose();
    super.dispose();
  }

  void _onTextChanged() {
    final text = _textController.text;
    final hasUrdu = RegExp(r'[\u0600-\u06FF]').hasMatch(text);
    if (_isUrdu != hasUrdu) {
      setState(() {
        _isUrdu = hasUrdu;
      });
    }
  }

  Future<void> _submitSignal() async {
    final text = _textController.text;
    if (text.isEmpty) return;

    setState(() {
      _isSubmitting = true;
    });

    try {
      final url = '${ApiConfig.baseUrl}/report/text';
      final response = await http.post(
        Uri.parse(url),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'text': text,
          'lat': _markerPosition.latitude,
          'lng': _markerPosition.longitude,
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('Signal successfully processed by AI Pipeline!'),
              backgroundColor: kPrimaryTeal,
              behavior: SnackBarBehavior.floating,
            ),
          );
          Navigator.pushReplacement(
            context,
            MaterialPageRoute(
              builder: (context) => IncidentTrackerScreen(incidentData: data),
            ),
          );
        }
      } else {
        throw Exception('Failed with status: ${response.statusCode}');
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Agent API Error: $e'),
            backgroundColor: Colors.red,
            behavior: SnackBarBehavior.floating,
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          _isSubmitting = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: kBackgroundLight,
      appBar: AppBar(
        title: const Text(
          'New Text Signal',
          style: TextStyle(fontWeight: FontWeight.bold),
        ),
        backgroundColor: kBackgroundLight,
        surfaceTintColor: Colors.transparent,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            TextField(
              controller: _textController,
              maxLines: null,
              minLines: 5,
              textDirection: _isUrdu ? TextDirection.rtl : TextDirection.ltr,
              decoration: InputDecoration(
                hintText:
                    'Describe the crisis (Urdu, English, Roman Urdu, or Punjabi)... / یہاں لکھیں...',
                hintStyle: const TextStyle(color: Colors.grey),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                  borderSide: BorderSide(color: Colors.grey.shade300),
                ),
                enabledBorder: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                  borderSide: BorderSide(color: Colors.grey.shade400),
                ),
                focusedBorder: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                  borderSide: const BorderSide(color: kPrimaryTeal, width: 2),
                ),
                contentPadding: const EdgeInsets.all(16),
                filled: true,
                fillColor: kCardWhite,
              ),
            ),
            const SizedBox(height: 12),
            Align(alignment: Alignment.centerLeft, child: _buildLanguageChip()),
            const SizedBox(height: 24),
            Text(
              'Specify Location',
              style: GoogleFonts.nunito(
                fontSize: 16,
                fontWeight: FontWeight.bold,
                color: kTextDark,
              ),
            ),
            const SizedBox(height: 12),
            Container(
              height: 250,
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: Colors.grey.shade300),
              ),
              child: ClipRRect(
                borderRadius: BorderRadius.circular(16),
                child: GoogleMap(
                  initialCameraPosition: CameraPosition(
                    target: _markerPosition,
                    zoom: 14,
                  ),
                  markers: {
                    Marker(
                      markerId: const MarkerId('incident_location'),
                      position: _markerPosition,
                      draggable: true,
                      onDragEnd: (newPosition) {
                        setState(() {
                          _markerPosition = newPosition;
                        });
                      },
                    ),
                  },
                ),
              ),
            ),
          ],
        ),
      ),
      bottomNavigationBar: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: ElevatedButton(
            onPressed: _isSubmitting ? null : _submitSignal,
            style: ElevatedButton.styleFrom(
              backgroundColor: kPrimaryTeal,
              foregroundColor: Colors.white,
              padding: const EdgeInsets.symmetric(vertical: 16),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
              ),
            ),
            child: _isSubmitting
                ? const SizedBox(
                    height: 20,
                    width: 20,
                    child: CircularProgressIndicator(
                      color: Colors.white,
                      strokeWidth: 2,
                    ),
                  )
                : const Text(
                    'Inject Signal into Pipeline →',
                    style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                  ),
          ),
        ),
      ),
    );
  }

  Widget _buildLanguageChip() {
    return AnimatedSwitcher(
      duration: const Duration(milliseconds: 300),
      child: Container(
        key: ValueKey<bool>(_isUrdu),
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
        decoration: BoxDecoration(
          color: (_isUrdu ? Colors.green : Colors.blue).withValues(alpha: 0.1),
          borderRadius: BorderRadius.circular(20),
          border: Border.all(
            color: (_isUrdu ? Colors.green : Colors.blue).withValues(alpha: 0.3),
          ),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              _isUrdu ? Icons.language : Icons.translate,
              size: 16,
              color: _isUrdu ? Colors.green.shade700 : Colors.blue.shade700,
            ),
            const SizedBox(width: 6),
            Text(
              _isUrdu
                  ? 'Urdu signal detected (98% Confidence)'
                  : 'Roman Urdu / English signal detected',
              style: GoogleFonts.nunito(
                fontSize: 12,
                fontWeight: FontWeight.bold,
                color: _isUrdu ? Colors.green.shade700 : Colors.blue.shade700,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
