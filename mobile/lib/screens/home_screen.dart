import 'package:flutter/material.dart';
import '../config/theme.dart';
import 'customer/chat_screen.dart';
import 'customer/bookings_screen.dart';
import 'customer/trace_screen.dart';
import 'provider/dashboard_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int _currentIndex = 0;
  bool _isCustomer = true; // Toggle between customer/provider view

  final List<Widget> _customerPages = [
    const ChatScreen(),
    const BookingsScreen(),
    const TraceScreen(),
  ];

  final List<Widget> _providerPages = [
    const ProviderDashboardScreen(),
    const BookingsScreen(),
    const TraceScreen(),
  ];

  @override
  Widget build(BuildContext context) {
    final pages = _isCustomer ? _customerPages : _providerPages;

    return Scaffold(
      body: AnimatedSwitcher(
        duration: const Duration(milliseconds: 300),
        child: pages[_currentIndex],
      ),
      bottomNavigationBar: Container(
        decoration: BoxDecoration(
          color: AppTheme.surface,
          border: Border(
            top: BorderSide(color: AppTheme.border.withValues(alpha: 0.3)),
          ),
        ),
        child: SafeArea(
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 8),
            child: Row(
              children: [
                // Role toggle
                GestureDetector(
                  onTap: () => setState(() {
                    _isCustomer = !_isCustomer;
                    _currentIndex = 0;
                  }),
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                    decoration: BoxDecoration(
                      color: _isCustomer
                          ? AppTheme.primary.withValues(alpha: 0.15)
                          : AppTheme.accent.withValues(alpha: 0.15),
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(
                        color: _isCustomer
                            ? AppTheme.primary.withValues(alpha: 0.3)
                            : AppTheme.accent.withValues(alpha: 0.3),
                      ),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(
                          _isCustomer ? Icons.person : Icons.work,
                          color: _isCustomer ? AppTheme.primary : AppTheme.accent,
                          size: 16,
                        ),
                        const SizedBox(width: 4),
                        Text(
                          _isCustomer ? 'Customer' : 'Provider',
                          style: TextStyle(
                            color: _isCustomer ? AppTheme.primary : AppTheme.accent,
                            fontSize: 11,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
                // Nav items
                Expanded(
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                    children: [
                      _navItem(0, _isCustomer ? Icons.chat_bubble_rounded : Icons.dashboard_rounded,
                          _isCustomer ? 'Chat' : 'Dashboard'),
                      _navItem(1, Icons.calendar_today_rounded, 'Bookings'),
                      _navItem(2, Icons.analytics_rounded, 'Traces'),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _navItem(int index, IconData icon, String label) {
    final isActive = _currentIndex == index;
    return GestureDetector(
      onTap: () => setState(() => _currentIndex = index),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        decoration: BoxDecoration(
          color: isActive ? AppTheme.primary.withValues(alpha: 0.15) : Colors.transparent,
          borderRadius: BorderRadius.circular(12),
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, color: isActive ? AppTheme.primary : AppTheme.textMuted, size: 22),
            const SizedBox(height: 2),
            Text(
              label,
              style: TextStyle(
                color: isActive ? AppTheme.primary : AppTheme.textMuted,
                fontSize: 10,
                fontWeight: isActive ? FontWeight.w600 : FontWeight.w400,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
