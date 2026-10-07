import i18n from "i18next";
import { initReactI18next } from "react-i18next";

import { resources } from "./resources";

export type SupportedLanguage = "vi" | "en" | "zh";

export const LANGUAGE_STORAGE_KEY = "autocve.language";

function isSupportedLanguage(value: string | null): value is SupportedLanguage {
  return value === "vi" || value === "en" || value === "zh";
}

function getInitialLanguage(): SupportedLanguage {
  if (typeof window === "undefined") {
    return "vi";
  }

  const storedLanguage = window.localStorage.getItem(LANGUAGE_STORAGE_KEY);
  return isSupportedLanguage(storedLanguage) ? storedLanguage : "vi";
}

void i18n.use(initReactI18next).init({
  resources,
  lng: getInitialLanguage(),
  fallbackLng: "vi",
  supportedLngs: ["vi", "en", "zh"],
  interpolation: {
    escapeValue: false,
  },
});

export function getCurrentLanguage(): SupportedLanguage {
  if (i18n.language === "en" || i18n.language === "zh") {
    return i18n.language;
  }
  return "vi";
}

export async function setAppLanguage(language: SupportedLanguage) {
  if (typeof window !== "undefined") {
    window.localStorage.setItem(LANGUAGE_STORAGE_KEY, language);
  }

  await i18n.changeLanguage(language);
}

export default i18n;
