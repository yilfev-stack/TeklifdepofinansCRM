import { Button } from "@/components/ui/button";
import { useTranslation } from "@/i18n/translations";
import { Globe } from "lucide-react";

const LanguageSwitcher = () => {
  const { currentLanguage, setLanguage } = useTranslation();

  return (
    <div className="flex items-center gap-2">
      <Globe className="h-4 w-4 text-muted-foreground" />
      <div className="flex gap-1">
        <Button
          variant={currentLanguage === 'tr' ? 'default' : 'ghost'}
          size="sm"
          onClick={() => setLanguage('tr')}
          className="text-xs px-3 h-8"
        >
          TR
        </Button>
        <Button
          variant={currentLanguage === 'en' ? 'default' : 'ghost'}
          size="sm"
          onClick={() => setLanguage('en')}
          className="text-xs px-3 h-8"
        >
          EN
        </Button>
      </div>
    </div>
  );
};

export default LanguageSwitcher;
