import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiService {
  // Change this to your backend URL (Cloud Run URL after deployment)
  static const String baseUrl = 'http://10.0.2.2:8080'; // Android emulator
  // static const String baseUrl = 'http://localhost:8080'; // iOS simulator / web
  // static const String baseUrl = 'https://your-cloud-run-url.run.app'; // Production

  String? _sessionId;

  String get sessionId => _sessionId ?? '';

  /// Send a chat message to the AI agent
  Future<Map<String, dynamic>> sendMessage(String message) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/chat'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'message': message,
          'session_id': _sessionId,
          'user_id': 'flutter_user',
        }),
      ).timeout(const Duration(seconds: 60));

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        _sessionId = data['session_id'];
        return data;
      } else {
        return {
          'response': 'Server error: ${response.statusCode}. Please try again.',
          'trace': [],
          'session_id': _sessionId ?? '',
        };
      }
    } catch (e) {
      return {
        'response': 'Connection error. Make sure the backend server is running.\nError: $e',
        'trace': [],
        'session_id': _sessionId ?? '',
      };
    }
  }

  /// Get all providers
  Future<List<dynamic>> getProviders() async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/providers'));
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return data['providers'] ?? [];
      }
    } catch (e) {
      // ignore
    }
    return [];
  }

  /// Get all bookings
  Future<List<dynamic>> getBookings() async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/bookings'));
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return data['bookings'] ?? [];
      }
    } catch (e) {
      // ignore
    }
    return [];
  }

  /// Get all agent traces
  Future<List<dynamic>> getTraces() async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/traces'));
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return data['traces'] ?? [];
      }
    } catch (e) {
      // ignore
    }
    return [];
  }

  /// Submit a dispute
  Future<Map<String, dynamic>> submitDispute(String bookingId, String complaint) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/dispute'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'booking_id': bookingId,
          'complaint': complaint,
          'session_id': _sessionId,
        }),
      ).timeout(const Duration(seconds: 60));

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      }
    } catch (e) {
      // ignore
    }
    return {'response': 'Failed to submit dispute', 'trace': []};
  }

  /// Health check
  Future<bool> isHealthy() async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/')).timeout(const Duration(seconds: 5));
      return response.statusCode == 200;
    } catch (e) {
      return false;
    }
  }

  /// Reset session
  void resetSession() {
    _sessionId = null;
  }
}
