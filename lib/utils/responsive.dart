import 'package:flutter/material.dart';

/// A simple responsive scaling utility for KHABAR.
/// 
/// Scales font sizes and spacing relative to a baseline screen width of 390px
/// (iPhone 14 / average mid-range Android) so that text never looks too
/// big on small phones or too small on large tablets.
///
/// Usage:
///   final r = Responsive(context);
///   Text('Hello', style: TextStyle(fontSize: r.sp(16)));
///   SizedBox(height: r.h(12));
///   Padding(padding: EdgeInsets.all(r.w(16)));
class Responsive {
  final BuildContext context;
  late final double _screenWidth;
  late final double _screenHeight;
  late final double _scaleFactor;

  static const double _baseWidth = 390.0;

  Responsive(this.context) {
    final size = MediaQuery.of(context).size;
    _screenWidth = size.width;
    _screenHeight = size.height;
    // Clamp scale between 0.85 (small phones) and 1.3 (large tablets)
    _scaleFactor = (_screenWidth / _baseWidth).clamp(0.85, 1.3);
  }

  /// Scale a font size
  double sp(double size) => size * _scaleFactor;

  /// Scale a horizontal dimension
  double w(double size) => size * (_screenWidth / _baseWidth);

  /// Scale a vertical dimension (use sparingly – prefer h: auto layout)
  double h(double size) => size * (_screenHeight / 844.0);

  /// Screen width
  double get screenWidth => _screenWidth;

  /// Screen height
  double get screenHeight => _screenHeight;

  /// Is a small phone (< 360px width)
  bool get isSmall => _screenWidth < 360;

  /// Is a tablet (>= 600px width)
  bool get isTablet => _screenWidth >= 600;
}
