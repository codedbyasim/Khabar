import 'package:flutter/material.dart';

/// Global language state that all screens can listen to.
class LanguageProvider extends ChangeNotifier {
  static final LanguageProvider _instance = LanguageProvider._internal();
  factory LanguageProvider() => _instance;
  LanguageProvider._internal();

  String _language = 'English';
  String _region = 'Islamabad, Capital Territory';

  String get language => _language;
  String get region => _region;

  void setLanguage(String lang) {
    if (_language != lang) {
      _language = lang;
      notifyListeners();
    }
  }

  void setRegion(String reg) {
    if (_region != reg) {
      _region = reg;
      notifyListeners();
    }
  }
}
