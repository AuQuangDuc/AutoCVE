import { Languages } from "lucide-react";
import { useTranslation } from "react-i18next";

import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { getCurrentLanguage, setAppLanguage, type SupportedLanguage } from "@/shared/i18n";

interface LanguageSwitcherProps {
  collapsed?: boolean;
}

export default function LanguageSwitcher({ collapsed = false }: LanguageSwitcherProps) {
  const { t, i18n } = useTranslation();
  const currentLanguage = getCurrentLanguage();

  const labels: Record<SupportedLanguage, string> = {
    vi: t("language.vietnamese"),
    en: t("language.english"),
    zh: t("language.chinese"),
  };

  const shortLabels: Record<SupportedLanguage, string> = {
    vi: "VI",
    en: "EN",
    zh: "中",
  };

  async function handleLanguageChange(language: SupportedLanguage) {
    if (language !== currentLanguage) {
      await setAppLanguage(language);
    }
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          type="button"
          variant="ghost"
          aria-label={t("language.switchTo")}
          title={collapsed ? t("language.switchTo") : undefined}
          className={`w-full justify-start gap-3 rounded-[22px] border border-slate-200/80 bg-white/70 px-3 py-3 text-slate-600 transition hover:border-[hsl(var(--primary)/0.35)] hover:bg-white hover:text-slate-900 ${collapsed ? "h-11 justify-center px-0" : "h-auto"}`}
        >
          <span className="flex h-9 w-9 items-center justify-center rounded-2xl bg-slate-100/80 text-slate-500">
            <Languages className="h-4 w-4" />
          </span>
          {!collapsed && (
            <span className="flex min-w-0 flex-1 items-center justify-between gap-3">
              <span className="truncate text-sm font-semibold">{t("language.label")}</span>
              <span className="rounded-full border border-slate-200 bg-[#f8f9f8] px-2 py-0.5 text-xs font-semibold text-slate-500">
                {shortLabels[currentLanguage]}
              </span>
            </span>
          )}
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align={collapsed ? "center" : "end"} className="min-w-40">
        {(["vi", "en", "zh"] as const).map((language) => (
          <DropdownMenuItem
            key={language}
            className={language === currentLanguage ? "font-semibold" : undefined}
            onSelect={() => void handleLanguageChange(language)}
          >
            <span className="mr-2 w-6 text-xs font-semibold text-muted-foreground">
              {shortLabels[language]}
            </span>
            {labels[language]}
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
