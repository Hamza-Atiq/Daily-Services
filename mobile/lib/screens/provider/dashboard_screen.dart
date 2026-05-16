import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../../config/theme.dart';
import '../../services/api_service.dart';

class ProviderDashboardScreen extends StatefulWidget {
  const ProviderDashboardScreen({super.key});

  @override
  State<ProviderDashboardScreen> createState() => _ProviderDashboardScreenState();
}

class _ProviderDashboardScreenState extends State<ProviderDashboardScreen> {
  final ApiService _api = ApiService();
  List<dynamic> _bookings = [];
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    setState(() => _loading = true);
    final bookings = await _api.getBookings();
    setState(() {
      _bookings = bookings;
      _loading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    final confirmed = _bookings.where((b) => b['status'] == 'confirmed').length;
    final completed = _bookings.where((b) => b['status'] == 'completed').length;
    final totalEarnings = _bookings
        .where((b) => b['status'] != 'cancelled')
        .fold<int>(0, (sum, b) => sum + ((b['total_price_pkr'] ?? 0) as int));

    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(gradient: AppTheme.heroGradient),
        child: SafeArea(
          child: RefreshIndicator(
            onRefresh: _loadData,
            color: AppTheme.primary,
            child: ListView(
              padding: const EdgeInsets.all(20),
              children: [
                // Header
                Row(
                  children: [
                    Container(
                      width: 48, height: 48,
                      decoration: BoxDecoration(
                        gradient: const LinearGradient(
                          colors: [AppTheme.accent, Color(0xFFD97706)],
                        ),
                        borderRadius: BorderRadius.circular(14),
                      ),
                      child: const Icon(Icons.work_rounded, color: Colors.white, size: 24),
                    ),
                    const SizedBox(width: 14),
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text('Provider Dashboard', style: Theme.of(context).textTheme.titleLarge),
                        Text('Manage your services', style: Theme.of(context).textTheme.bodySmall),
                      ],
                    ),
                  ],
                ).animate().fadeIn(duration: 400.ms),

                const SizedBox(height: 24),

                // Stats cards
                Row(
                  children: [
                    Expanded(child: _buildStatCard('Active Jobs', '$confirmed', Icons.work_outline, AppTheme.primary, 0)),
                    const SizedBox(width: 12),
                    Expanded(child: _buildStatCard('Completed', '$completed', Icons.check_circle_outline, AppTheme.accent, 1)),
                    const SizedBox(width: 12),
                    Expanded(child: _buildStatCard('Earnings', 'PKR ${totalEarnings > 1000 ? '${(totalEarnings / 1000).toStringAsFixed(1)}k' : totalEarnings}', Icons.account_balance_wallet, AppTheme.info, 2)),
                  ],
                ),

                const SizedBox(height: 24),

                // Today's schedule
                Text('Upcoming Jobs', style: Theme.of(context).textTheme.titleMedium)
                    .animate().fadeIn(duration: 300.ms, delay: 300.ms),
                const SizedBox(height: 12),

                if (_loading)
                  const Center(child: Padding(
                    padding: EdgeInsets.all(40),
                    child: CircularProgressIndicator(color: AppTheme.primary),
                  ))
                else if (_bookings.isEmpty)
                  Container(
                    padding: const EdgeInsets.all(32),
                    decoration: AppTheme.glassCard,
                    child: Column(
                      children: [
                        const Icon(Icons.inbox_rounded, color: AppTheme.textMuted, size: 48),
                        const SizedBox(height: 12),
                        Text('No jobs yet', style: Theme.of(context).textTheme.titleMedium),
                        const SizedBox(height: 4),
                        Text('Jobs will appear here when customers book your services.',
                            style: Theme.of(context).textTheme.bodySmall, textAlign: TextAlign.center),
                      ],
                    ),
                  ).animate().fadeIn(duration: 300.ms, delay: 400.ms)
                else
                  ...List.generate(
                    _bookings.length,
                    (i) => _buildJobCard(_bookings[i], i),
                  ),

                const SizedBox(height: 24),

                // Quick tips
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: AppTheme.primary.withValues(alpha: 0.08),
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(color: AppTheme.primary.withValues(alpha: 0.2)),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Icon(Icons.lightbulb_outline, color: AppTheme.primary.withValues(alpha: 0.8), size: 18),
                          const SizedBox(width: 8),
                          const Text('Optimization Tips', style: TextStyle(color: AppTheme.primary, fontSize: 14, fontWeight: FontWeight.w600)),
                        ],
                      ),
                      const SizedBox(height: 8),
                      const Text(
                        '\u{2022} Keep your availability updated for better matching\n'
                        '\u{2022} Quick response time improves your ranking\n'
                        '\u{2022} Morning slots (9-12 AM) have highest demand',
                        style: TextStyle(color: AppTheme.textSecondary, fontSize: 12, height: 1.6),
                      ),
                    ],
                  ),
                ).animate().fadeIn(duration: 300.ms, delay: 500.ms),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildStatCard(String label, String value, IconData icon, Color color, int index) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.08),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: color.withValues(alpha: 0.2)),
      ),
      child: Column(
        children: [
          Icon(icon, color: color, size: 22),
          const SizedBox(height: 8),
          Text(value, style: TextStyle(color: color, fontSize: 18, fontWeight: FontWeight.w700)),
          const SizedBox(height: 2),
          Text(label, style: const TextStyle(color: AppTheme.textMuted, fontSize: 10)),
        ],
      ),
    ).animate().fadeIn(duration: 300.ms, delay: Duration(milliseconds: 100 + index * 100)).scale(begin: const Offset(0.9, 0.9));
  }

  Widget _buildJobCard(dynamic booking, int index) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: AppTheme.providerCard,
      child: Row(
        children: [
          Container(
            width: 44, height: 44,
            decoration: BoxDecoration(
              color: AppTheme.primary.withValues(alpha: 0.15),
              borderRadius: BorderRadius.circular(12),
            ),
            child: const Icon(Icons.build_rounded, color: AppTheme.primary, size: 22),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  (booking['service_type'] ?? '').toString().replaceAll('_', ' ').toUpperCase(),
                  style: const TextStyle(color: AppTheme.textPrimary, fontSize: 14, fontWeight: FontWeight.w600),
                ),
                const SizedBox(height: 2),
                Text(
                  '${booking['date'] ?? ''} at ${booking['time'] ?? ''} - ${booking['location_sector'] ?? ''}',
                  style: const TextStyle(color: AppTheme.textSecondary, fontSize: 12),
                ),
              ],
            ),
          ),
          Column(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              Text(
                'PKR ${booking['total_price_pkr'] ?? 0}',
                style: const TextStyle(color: AppTheme.primary, fontSize: 14, fontWeight: FontWeight.w700),
              ),
              const SizedBox(height: 4),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                decoration: BoxDecoration(
                  color: AppTheme.primary.withValues(alpha: 0.1),
                  borderRadius: BorderRadius.circular(4),
                ),
                child: Text(
                  (booking['status'] ?? '').toString().toUpperCase(),
                  style: const TextStyle(color: AppTheme.primary, fontSize: 9, fontWeight: FontWeight.w700),
                ),
              ),
            ],
          ),
        ],
      ),
    ).animate().fadeIn(duration: 300.ms, delay: Duration(milliseconds: 300 + index * 100)).slideX(begin: 0.1);
  }
}
