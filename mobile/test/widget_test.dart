import 'package:flutter_test/flutter_test.dart';
import 'package:service_app/main.dart';

void main() {
  testWidgets('App loads', (WidgetTester tester) async {
    await tester.pumpWidget(const ServiceApp());
    expect(find.text('Service Assistant'), findsOneWidget);
  });
}
